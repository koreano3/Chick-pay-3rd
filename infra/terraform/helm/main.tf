# ---------------- Remote States ------------------
data "terraform_remote_state" "cicd" {
  backend = "local"
  config = {
    path = "../eks/cicd/terraform.tfstate"
  }
}

data "terraform_remote_state" "service" {
  backend = "local"
  config = {
    path = "../eks/service/terraform.tfstate"
  }
}

data "terraform_remote_state" "iam" {
  backend = "local"
  config = {
    path = "../iam/terraform.tfstate"
  }
}

data "terraform_remote_state" "vpc" {
  backend = "local"
  config = {
    path = "../vpc/terraform.tfstate"
  }
}

# ---------------- EKS Auth ------------------
data "aws_eks_cluster_auth" "cicd" {
  name = data.terraform_remote_state.cicd.outputs.cluster_name
}

data "aws_eks_cluster_auth" "service" {
  name = data.terraform_remote_state.service.outputs.cluster_name
}

# ---------------- Providers ------------------
provider "kubernetes" {
  alias                  = "cicd"
  host                   = data.terraform_remote_state.cicd.outputs.cluster_endpoint
  token                  = data.aws_eks_cluster_auth.cicd.token
  cluster_ca_certificate = base64decode(data.terraform_remote_state.cicd.outputs.cluster_certificate_authority_data)
}

provider "helm" {
  alias = "cicd"
  kubernetes {
    host                   = data.terraform_remote_state.cicd.outputs.cluster_endpoint
    token                  = data.aws_eks_cluster_auth.cicd.token
    cluster_ca_certificate = base64decode(data.terraform_remote_state.cicd.outputs.cluster_certificate_authority_data)
  }
}

provider "kubernetes" {
  alias                  = "service"
  host                   = data.terraform_remote_state.service.outputs.cluster_endpoint
  token                  = data.aws_eks_cluster_auth.service.token
  cluster_ca_certificate = base64decode(data.terraform_remote_state.service.outputs.cluster_certificate_authority_data)
}

provider "helm" {
  alias = "service"
  kubernetes {
    host                   = data.terraform_remote_state.service.outputs.cluster_endpoint
    token                  = data.aws_eks_cluster_auth.service.token
    cluster_ca_certificate = base64decode(data.terraform_remote_state.service.outputs.cluster_certificate_authority_data)
  }
}

# ---------------- CICD 클러스터 ------------------
resource "kubernetes_namespace" "argocd" {
  provider = kubernetes.cicd
  metadata {
    name = "argocd"
  }
}

resource "helm_release" "argocd" {
  provider   = helm.cicd
  name       = "argo-cd"
  namespace  = kubernetes_namespace.argocd.metadata[0].name
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  version    = "5.51.6"
  create_namespace = false
  depends_on = [kubernetes_namespace.argocd]
}

# ---------------- 서비스 클러스터 ------------------
resource "kubernetes_namespace" "monitoring" {
  provider = kubernetes.service
  metadata {
    name = "monitoring"
  }
}

resource "helm_release" "prometheus" {
  provider   = helm.service
  name       = "kube-prometheus-stack"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  version    = "58.2.0"
  create_namespace = false
  depends_on = [helm_release.aws_load_balancer_controller]
}

# ---------------- ALB용 IRSA & ServiceAccount ------------------
resource "aws_iam_role" "alb_controller" {
  name = "alb-controller-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Federated = data.terraform_remote_state.service.outputs.oidc_provider_arn
      },
      Action = "sts:AssumeRoleWithWebIdentity",
      Condition = {
        StringEquals = {
          "${replace(data.terraform_remote_state.service.outputs.oidc_provider_url, "https://", "")}:sub" = "system:serviceaccount:alb-system:aws-load-balancer-controller"
        }
      }
    }]
  })
}

resource "aws_iam_policy" "alb_policy" {
  name   = "AWSLoadBalancerControllerIAMPolicy"
  policy = file("iam-policy.json")
}

resource "aws_iam_role_policy_attachment" "alb_attach" {
  role       = aws_iam_role.alb_controller.name
  policy_arn = aws_iam_policy.alb_policy.arn
}

resource "kubernetes_namespace" "alb" {
  provider = kubernetes.service
  metadata {
    name = "alb-system"
  }
}

resource "kubernetes_service_account" "alb_sa" {
  provider = kubernetes.service
  metadata {
    name      = "aws-load-balancer-controller"
    namespace = kubernetes_namespace.alb.metadata[0].name
    annotations = {
      "eks.amazonaws.com/role-arn" = aws_iam_role.alb_controller.arn
    }
  }
}

resource "helm_release" "aws_load_balancer_controller" {
  provider   = helm.service
  name       = "aws-load-balancer-controller"
  namespace  = kubernetes_namespace.alb.metadata[0].name
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  version    = "1.7.1"
  create_namespace = false

  set {
    name  = "clusterName"
    value = data.terraform_remote_state.service.outputs.cluster_name
  }

  set {
    name  = "region"
    value = "ap-northeast-2"
  }

  set {
    name  = "vpcId"
    value = data.terraform_remote_state.service.outputs.vpc_id
  }

  set {
    name  = "serviceAccount.create"
    value = "false"
  }

  set {
    name  = "serviceAccount.name"
    value = kubernetes_service_account.alb_sa.metadata[0].name
  }

  depends_on = [kubernetes_service_account.alb_sa]
}
