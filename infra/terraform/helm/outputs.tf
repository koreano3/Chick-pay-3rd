output "argocd_helm_release_name" {
  description = "The Helm release name for ArgoCD"
  value       = helm_release.argocd.name
}

output "argocd_namespace" {
  description = "Namespace where ArgoCD is installed"
  value       = kubernetes_namespace.argocd.metadata[0].name
}
