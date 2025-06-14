# provider "aws" {
#   region = var.region
# }

# # S3 Bucket for Terraform State
# resource "aws_s3_bucket" "tf_state" {
#   bucket = var.bucket_name
#   force_destroy = true

#   tags = {
#     Name = "terraform-state"
#     Environment = "dev"
#   }
# }

# # Enable versioning for backup
# resource "aws_s3_bucket_versioning" "versioning" {
#   bucket = aws_s3_bucket.tf_state.id

#   versioning_configuration {
#     status = "Enabled"
#   }
# }

# # Server-side encryption
# resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
#   bucket = aws_s3_bucket.tf_state.id

#   rule {
#     apply_server_side_encryption_by_default {
#       sse_algorithm = "AES256"
#     }
#   }
# }

# # Optional: DynamoDB for state locking
# resource "aws_dynamodb_table" "tf_lock" {
#   name         = var.lock_table_name
#   billing_mode = "PAY_PER_REQUEST"
#   hash_key     = "LockID"

#   attribute {
#     name = "LockID"
#     type = "S"
#   }

#   tags = {
#     Name = "terraform-lock"
#     Environment = "dev"
#   }
# }
