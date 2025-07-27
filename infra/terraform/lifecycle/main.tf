provider "aws" {
  region  = "ap-northeast-2"
}

# 버킷 생성
resource "aws_s3_bucket" "log_bucket" {
  bucket = var.bucket_name
}

# Terraform 로그용 Lifecycle Rule
resource "aws_s3_bucket_lifecycle_configuration" "terraform_logs" {
  bucket = aws_s3_bucket.log_bucket.bucket

  depends_on = [aws_s3_bucket.log_bucket]

  rule {
    id     = "terraform-logs-to-glacier"
    status = "Enabled"

    filter {
      prefix = "logs/terraform/"
    }

    transition {
      days          = var.transition_days
      storage_class = "GLACIER"
    }

    expiration {
      days = var.expire_days
    }
  }
}

# Ansible 로그용 Lifecycle Rule
resource "aws_s3_bucket_lifecycle_configuration" "ansible_logs" {
  bucket = var.bucket_name

  depends_on = [aws_s3_bucket.log_bucket]

  rule {
    id     = "ansible-logs-to-glacier"
    status = "Enabled"

    filter {
      prefix = "logs/ansible/"
    }

    transition {
      days          = var.transition_days
      storage_class = "GLACIER"
    }

    expiration {
      days = var.expire_days
    }
  }
}

# 전체 로그용 Lifecycle Rule
resource "aws_s3_bucket_lifecycle_configuration" "all_logs" {
  bucket = var.bucket_name

  depends_on = [aws_s3_bucket.log_bucket]

  rule {
    id     = "all-logs-to-glacier"
    status = "Enabled"

    filter {
      prefix = "logs/"
    }

    transition {
      days          = var.transition_days
      storage_class = "GLACIER"
    }

    expiration {
      days = var.expire_days
    }
  }
}
