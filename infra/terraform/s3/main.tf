# ────────────────────────────────────────────────
# AWS Provider
# ────────────────────────────────────────────────
provider "aws" {
  region  = "ap-northeast-2"
  profile = "eomsigi"
}

# ────────────────────────────────────────────────
# KMS Key for SSE-KMS Encryption
# ────────────────────────────────────────────────
# resource "aws_kms_key" "velero" {
#   description             = "KMS key for Velero S3 bucket encryption"
#   deletion_window_in_days = 10
#   enable_key_rotation     = true
# }

# resource "aws_kms_alias" "velero" {
#   name          = "alias/velero-backup-key"
#   target_key_id = aws_kms_key.velero.key_id
# }

# # ────────────────────────────────────────────────
# # S3 Bucket for Velero
# # ────────────────────────────────────────────────
# resource "aws_s3_bucket" "velero" {
#   bucket        = var.bucket_name
#   force_destroy = true  # 옵션: terraform destroy 시 객체까지 제거

#   tags = {
#     Name        = "velero-backup-bucket"
#     Environment = "prod"
#   }
# }

# resource "aws_s3_bucket_versioning" "velero" {
#   bucket = aws_s3_bucket.velero.id

#   versioning_configuration {
#     status = "Enabled"
#   }
# }

# resource "aws_s3_bucket_server_side_encryption_configuration" "velero" {
#   bucket = aws_s3_bucket.velero.id

#   rule {
#     apply_server_side_encryption_by_default {
#       sse_algorithm     = "aws:kms"
#       kms_master_key_id = aws_kms_key.velero.arn
#     }
#   }

#   depends_on = [aws_kms_key.velero]
# }

# resource "aws_s3_bucket_public_access_block" "velero" {
#   bucket = aws_s3_bucket.velero.id

#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }

# resource "aws_s3_bucket_lifecycle_configuration" "velero" {
#   bucket = aws_s3_bucket.velero.id

#   rule {
#     id     = "auto-expire"
#     status = "Enabled"

#     expiration {
#       days = var.expire_after_days
#     }
#   }
# }
