# CICD 클러스터 OIDC ARN 출력
output "cicd_oidc_provider_arn" {
  value = data.aws_iam_openid_connect_provider.cicd.arn
}

# 서비스 클러스터 OIDC ARN 출력
output "service_oidc_provider_arn" {
  value = data.aws_iam_openid_connect_provider.service.arn
}

# CICD 클러스터 OIDC URL 출력 (IRSA 연결 시 유용)
output "cicd_oidc_url" {
  value = data.aws_eks_cluster.cicd.identity[0].oidc[0].issuer
}

# 서비스 클러스터 OIDC URL 출력
output "service_oidc_url" {
  value = data.aws_eks_cluster.service.identity[0].oidc[0].issuer
}

# output "velero_irsa_role_arn" {
#   value = aws_iam_role.velero_irsa_role.arn
# }