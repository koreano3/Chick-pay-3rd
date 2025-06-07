
# ---------------- Remote State ------------------
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




# resource "kubernetes_namespace" "velero" {
#   provider = kubernetes.service
#   metadata {
#     name = "velero"
#   }
# }

# resource "helm_release" "velero" {
#   provider   = helm.service
#   name       = "velero"
#   namespace  = kubernetes_namespace.velero.metadata[0].name
#   repository = "https://vmware-tanzu.github.io/helm-charts"
#   chart      = "velero"
#   version    = "6.0.0"
#   create_namespace = false
  
#   values = [templatefile("${path.module}/values/velero.yaml", {
#   irsa_role_arn = data.terraform_remote_state.iam.outputs.velero_irsa_role_arn,
#   region = "ap-northeast-2",
#   bucket = "velero-backup-for-chickpay",
#   provider = "aws"
# })
# ]

# depends_on = [kubernetes_namespace.velero]
# }

# AWS load Balancer Controller
resource "kubernetes_namespace" "alb" {
  provider = kubernetes.service
  metadata {
    name = "alb-system"
  }
}

resource "helm_release" "aws_load_balancer_controller" {
  provider   = helm.service
  name       = "aws-load-balancer-controller"
  namespace  = kubernetes_namespace.alb.metadata[0].name
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  version    = "1.7.1" # (최신 버전 확인 후 사용)
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
    value = "aws-load-balancer-controller"
  }
}