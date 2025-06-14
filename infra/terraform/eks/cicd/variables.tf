# 클러스터 리전
variable "region" {
  default = "ap-northeast-2"
}

# 클러스터 이름
variable "cluster_name" {
  default = "eks-infra"
}

# 클러스터 버전
variable "cluster_version" {
  default = "1.29"
}

variable "vpc_id" {
  description = "VPC ID for the CICD EKS cluster"
  type        = string
}
