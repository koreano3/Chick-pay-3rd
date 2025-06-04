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


# Velero용 IAM Policy! 
resource "aws_iam_policy" "velero_policy" {
  name        = "velero-s3-kms-access-policy"
  description = "Policy for Velero to access S3 and decrypt with KMS"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        Resource = [
          "arn:aws:s3:::${var.velero_s3_bucket_name}",
          "arn:aws:s3:::${var.velero_s3_bucket_name}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:GenerateDataKey",
          "kms:DescribeKey"
        ],
        Resource = data.terraform_remote_state.s3.outputs.velero_kms_key_arn
      }
    ]
  })
}

# Velero용 IAM Role
resource "aws_iam_role" "velero_irsa_role" {
  name = "velero-irsa-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Federated = data.aws_iam_openid_connect_provider.cicd.arn
        },
        Action = "sts:AssumeRoleWithWebIdentity",
        Condition = {
          StringEquals = {
            "${replace(data.aws_eks_cluster.service.identity[0].oidc[0].issuer, "https://", "")}:sub" = "system:serviceaccount:velero:velero"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "velero_attach" {
  role       = aws_iam_role.velero_irsa_role.name
  policy_arn = aws_iam_policy.velero_policy.arn
}