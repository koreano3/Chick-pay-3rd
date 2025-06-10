variable "bucket_name" {
  description = "Lifecycle Rule을 적용할 대상 S3 버킷 이름"
  type        = string
}

variable "transition_days" {
  description = "Glacier로 전환되기까지의 일수"
  type        = number
  default     = 7
}

variable "expire_days" {
  description = "객체가 S3에서 삭제되기까지의 일수"
  type        = number
  default     = 365
}
