# ----- Remote state for CICD 클러스터 -----
data "terraform_remote_state" "cicd" {
  backend = "local"
  config = {
    path = "../eks/cicd/terraform.tfstate"
  }
}

data "aws_eks_cluster_auth" "cicd" {
  name = data.terraform_remote_state.cicd.outputs.cluster_name
}

provider "kubernetes" {
  alias = "cicd"
  host  = data.terraform_remote_state.cicd.outputs.cluster_endpoint
  token = data.aws_eks_cluster_auth.cicd.token
  cluster_ca_certificate = base64decode(
    data.terraform_remote_state.cicd.outputs.cluster_certificate_authority_data
  )
}

provider "helm" {
  alias = "cicd"
  kubernetes {
    host  = data.terraform_remote_state.cicd.outputs.cluster_endpoint
    token = data.aws_eks_cluster_auth.cicd.token
    cluster_ca_certificate = base64decode(
      data.terraform_remote_state.cicd.outputs.cluster_certificate_authority_data
    )
  }
}

resource "kubernetes_namespace" "argocd" {
  provider = kubernetes.cicd
  metadata {
    name = var.argocd_namespace
  }
}

resource "helm_release" "argocd" {
  provider   = helm.cicd
  name       = "argo-cd"
  namespace  = var.argocd_namespace
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  version    = var.argocd_chart_version
  create_namespace = false

  depends_on = [kubernetes_namespace.argocd]
}
