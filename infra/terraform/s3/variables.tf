variable "bucket_name" {
  description = "S3 bucket name for Velero backup"
  type        = string
}

variable "expire_after_days" {
  description = "Number of days to retain backup objects"
  type        = number
  default     = 90
}
