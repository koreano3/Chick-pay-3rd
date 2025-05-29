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

# CICD 클러스터 provider
provider "helm" {
  alias = "cicd"
  kubernetes {
    host                   = data.terraform_remote_state.cicd.outputs.cluster_endpoint
    cluster_ca_certificate = base64decode(data.terraform_remote_state.cicd.outputs.cluster_certificate_authority_data)
    token                  = data.terraform_remote_state.cicd.outputs.cluster_token
  }
}

provider "kubernetes" {
  alias = "cicd"
  host                   = data.terraform_remote_state.cicd.outputs.cluster_endpoint
  cluster_ca_certificate = base64decode(data.terraform_remote_state.cicd.outputs.cluster_certificate_authority_data)
  token                  = data.terraform_remote_state.cicd.outputs.cluster_token
}

# 서비스 클러스터 provider
provider "helm" {
  alias = "service"
  kubernetes {
    host                   = data.terraform_remote_state.service.outputs.cluster_endpoint
    cluster_ca_certificate = base64decode(data.terraform_remote_state.service.outputs.cluster_certificate_authority_data)
    token                  = data.terraform_remote_state.service.outputs.cluster_token
  }
}

provider "kubernetes" {
  alias = "service"
  host                   = data.terraform_remote_state.service.outputs.cluster_endpoint
  cluster_ca_certificate = base64decode(data.terraform_remote_state.service.outputs.cluster_certificate_authority_data)
  token                  = data.terraform_remote_state.service.outputs.cluster_token
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
}

# ---------------- 서비스 클러스터 ------------------

resource "kubernetes_namespace" "monitoring" {
  provider = kubernetes.service
  metadata {
    name = "monitoring"
  }
}

resource "kubernetes_namespace" "velero" {
  provider = kubernetes.service
  metadata {
    name = "velero"
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
}

resource "helm_release" "grafana" {
  provider   = helm.service
  name       = "grafana"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  repository = "https://grafana.github.io/helm-charts"
  chart      = "grafana"
  version    = "7.3.10"
  create_namespace = false
}

resource "helm_release" "velero" {
  provider   = helm.service
  name       = "velero"
  namespace  = kubernetes_namespace.velero.metadata[0].name
  repository = "https://vmware-tanzu.github.io/helm-charts"
  chart      = "velero"
  version    = "6.0.0"
  create_namespace = false
  
  values = [templatefile("${path.module}/values/velero.yaml", {
    irsa_role_arn = data.terraform_remote_state.iam.outputs.velero_irsa_role_arn
  
  })]
}