output "argocd_helm_release_name" {
  description = "The Helm release name for ArgoCD"
  value       = helm_release.argocd.name
}

output "argocd_namespace" {
  description = "Namespace where ArgoCD is installed"
  value       = kubernetes_namespace.argocd.metadata[0].name
}

output "prometheus_helm_release_name" {
  description = "Prometheus Helm release"
  value       = helm_release.prometheus.name
}

output "alb_namespace" {
  value = kubernetes_namespace.alb.metadata[0].name
}

output "alb_controller_release" {
  value = helm_release.aws_load_balancer_controller.name
}
