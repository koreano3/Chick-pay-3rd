output "argocd_namespace" {
  description = "Namespace where ArgoCD is installed"
  value       = kubernetes_namespace.argocd.metadata[0].name
}

output "argocd_release_name" {
  description = "ArgoCD Helm release name"
  value       = helm_release.argocd.name
}
