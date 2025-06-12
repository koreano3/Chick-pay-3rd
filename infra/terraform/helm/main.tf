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

resource "aws_prometheus_workspace" "main" {
  alias = "my-eks-amp"
}

#TODO: 비활성화 -> 활성화 해야함
# resource "helm_release" "adot_collector" {
#   name       = "adot-exporter-for-eks-on-ec2"
#   repository = "https://aws-observability.github.io/aws-otel-helm-charts"
#   chart      = "adot-exporter-for-eks-on-ec2"
#   version    = "0.22.0"  # 최신 릴리즈 버전 기준 또는 필요 버전 입력
#   namespace  = kubernetes_namespace.monitoring.metadata[0].name
#   create_namespace = false

#   values = [
#     templatefile("${path.module}/values/adot-values.tpl.yaml", {
#       cluster_name     = data.terraform_remote_state.service.outputs.cluster_name
#       amp_workspace_id = aws_prometheus_workspace.main.id
#       adot_amp_role_arn= aws_iam_role.adot_amp.arn
#     })
#   ]

#   depends_on = [
#     kubernetes_namespace.monitoring,
#     aws_prometheus_workspace.main,
#     aws_iam_role.adot_amp
#   ]
# }

resource "kubernetes_namespace" "grafana" {
  provider = kubernetes.service
  metadata {
    name = "grafana"
  }
}
# resource "helm_release" "grafana" {
#   provider   = helm.service
#   name       = "grafana"
#   namespace  = kubernetes_namespace.grafana.metadata[0].name
#   repository = "https://grafana.github.io/helm-charts"
#   chart      = "grafana"
#   version    = "7.3.9"
#   create_namespace = false

#   set {
#     name  = "adminUser"
#     value = "admin"
#   }

#   set {
#     name  = "adminPassword"
#     value = "changeme"
#   }

#   set {
#     name  = "service.type"
#     value = "LoadBalancer"
#   }

#   set {
#     name  = "persistence.enabled"
#     value = "true"
#   }

#   set {
#     name  = "persistence.size"
#     value = "5Gi"
#   }

#   depends_on = [kubernetes_namespace.grafana]
# }

# resource "kubernetes_config_map" "grafana_datasource" {
#   provider = kubernetes.service
#   metadata {
#     name      = "grafana-datasources"
#     namespace = kubernetes_namespace.grafana.metadata[0].name
#     labels = {
#       grafana_datasource = "1"
#     }
#   }

  # data = {
  #   "prometheus.yaml" = yamlencode({
  #     apiVersion = 1
  #     datasources = [{
  #       name      = "AMP"
  #       type      = "prometheus"
  #       access    = "proxy"
  #       url       = "https://aps-workspaces.ap-northeast-2.amazonaws.com/workspaces/${aws_prometheus_workspace.main.id}"
  #       jsonData  = {
  #         sigV4Auth     = true
  #         sigV4AuthType = "default"
  #         sigV4Region   = "ap-northeast-2"
  #       }
  #     }]
  #   })
  # }

#   depends_on = [helm_release.grafana]
# }
# # ---------------- ADOT AMP용 IAM Role (IRSA) ------------------
# resource "aws_iam_role" "adot_amp" {
#   name = "adot-amp-role"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect = "Allow"
#       Principal = {
#         Federated = data.terraform_remote_state.service.outputs.oidc_provider_arn
#       }
#       Action = "sts:AssumeRoleWithWebIdentity"
#       Condition = {
#         StringEquals = {
#           "${data.terraform_remote_state.service.outputs.oidc_provider_url}:sub" = "system:serviceaccount:monitoring:adot-collector-sa"
#         }
#       }
#     }]
#   })
# }

# resource "aws_iam_role_policy_attachment" "adot_amp_attach" {
#   role       = aws_iam_role.adot_amp.name
#   policy_arn = "arn:aws:iam::aws:policy/AmazonPrometheusRemoteWriteAccess"
# }


# ---------------- ALB용 IAM Role (IRSA) ------------------

# ---------------- AWS Load Balancer Controller ------------------
# resource "kubernetes_namespace" "alb" {
#   provider = kubernetes.service
#   metadata {
#     name = "kube-system"
#   }
# }

resource "kubernetes_service_account" "alb_controller" {
  provider = kubernetes.service
  metadata {
    name      = "aws-load-balancer-controller"
    namespace = "kube-system"
    annotations = {
      "eks.amazonaws.com/role-arn" = var.alb_controller_iam_role_arn
    }
  }
}

resource "helm_release" "aws_load_balancer_controller" {
  provider   = helm.service
  name       = "aws-load-balancer-controller"
  namespace  = "kube-system"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  version    = "1.7.1"
  create_namespace = false

  depends_on = [
    kubernetes_service_account.alb_controller
  ]

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = var.alb_controller_iam_role_arn
  }

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