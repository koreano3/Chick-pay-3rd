# ArgoCD 설치 namespace
variable "argocd_namespace" {
  description = "Namespace for ArgoCD deployment"
  type        = string
  default     = "argocd"
}

# Helm chart version
variable "argocd_chart_version" {
  description = "ArgoCD Helm chart version"
  type        = string
  default     = "5.51.6"
}

variable "alb_controller_iam_role_arn" {
  description = "Pre-created IAM role for ALB controller"
  type        = string
}