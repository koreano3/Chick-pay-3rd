# CICD 클러스터용 OIDC Provider (조회 방식으로 수정)
data "aws_iam_openid_connect_provider" "cicd" {
  url = data.aws_eks_cluster.cicd.identity[0].oidc[0].issuer
}

# 서비스 클러스터용 OIDC Provider (조회 방식으로 수정)
data "aws_iam_openid_connect_provider" "service" {
  url = data.aws_eks_cluster.service.identity[0].oidc[0].issuer
}

# EKS 클러스터 정보 불러오기

# CICD
data "aws_eks_cluster" "cicd" {
  name = var.cicd_cluster_name
}
data "aws_eks_cluster_auth" "cicd" {
  name = var.cicd_cluster_name
}

# 서비스
data "aws_eks_cluster" "service" {
  name = var.service_cluster_name
}
data "aws_eks_cluster_auth" "service" {
  name = var.service_cluster_name
}

data "terraform_remote_state" "s3" {
  backend = "local" # 또는 S3 backend 사용 시에 맞게 변경
  config = {
    path = "../s3/terraform.tfstate"
  }
}