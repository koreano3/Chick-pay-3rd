output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

# output "kubeconfig" {
#   value = module.eks.kubeconfig_filename
# }

output "cluster_security_group_id" {
  value = module.eks.cluster_security_group_id
}

output "cluster_oidc_issuer_url" {
  value = module.eks.cluster_oidc_issuer_url
}

output "cluster_certificate_authority_data" {
  value = module.eks.cluster_certificate_authority_data
}

output "cluster_token" {
  value = data.aws_eks_cluster_auth.this.token  # ✅ 수정
  sensitive = true
}

