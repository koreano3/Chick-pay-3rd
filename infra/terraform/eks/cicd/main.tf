terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# ✅ vpc 모듈에서 생성한 VPC와 서브넷 정보 가져오기
data "terraform_remote_state" "vpc" {
  backend = "local"
  config = {
    path = "../../vpc/terraform.tfstate"
  }
}

# ✅ EKS 클러스터 생성
module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  version         = "~> 20.0"

  cluster_name    = var.cluster_name         # eks-infra
  cluster_version = var.cluster_version      # 1.29

  cluster_endpoint_public_access       = true     # 퍼블릭 ON
  cluster_endpoint_private_access      = true     # 프라이빗도 ON

  vpc_id     = data.terraform_remote_state.vpc.outputs.vpc_id
  subnet_ids = data.terraform_remote_state.vpc.outputs.public_subnet_ids

  enable_irsa = true  # OIDC IRSA 활성화 → ArgoCD, Helm 연동용

  eks_managed_node_groups = {
    cicd-nodes = {
      instance_types = ["t3.medium"]    # 필요하면 t3.large로 변경 가능
      desired_size   = 2
      min_size       = 1
      max_size       = 3
    }
  }

  tags = {
    Name    = var.cluster_name
    Purpose = "cicd-cluster"
  }
}
