output "argocd_namespace" {
  description = "Namespace where ArgoCD is installed"
  value       = kubernetes_namespace.argocd.metadata[0].name
}

output "argocd_release_name" {
  description = "ArgoCD Helm release name"
  value       = helm_release.argocd.name
}

output "prometheus_namespace" {
  description = "Namespace where Prometheus is installed"
  value       = kubernetes_namespace.monitoring.metadata[0].name
}

output "prometheus_release_name" {
  description = "Prometheus Helm release name"
  value       = helm_release.prometheus.name
}

output "alb_controller_namespace" {
  description = "Namespace where AWS Load Balancer Controller is installed"
  value       = kubernetes_namespace.alb.metadata[0].name
}

output "alb_controller_release_name" {
  description = "ALB Controller Helm release name"
  value       = helm_release.aws_load_balancer_controller.name
}

output "vpc_id" {
  value = data.terraform_remote_state.vpc.outputs.vpc_id
}
