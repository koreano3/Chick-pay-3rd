variable "cicd_cluster_name" {
  type        = string
  description = "Name of the CICD EKS cluster"
}

variable "service_cluster_name" {
  type        = string
  description = "Name of the service EKS cluster"
}

variable "velero_s3_bucket_name" {
  type        = string
  description = "Name of the S3 bucket used by Velero"
}

