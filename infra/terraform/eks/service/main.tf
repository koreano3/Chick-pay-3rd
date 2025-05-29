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

# ✅ 앞에서 만든 VPC 상태 참조
data "terraform_remote_state" "vpc" {
  backend = "local"
  config = {
    path = "../../vpc/terraform.tfstate"
  }
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_name
}



# ✅ 서비스용 EKS 클러스터
module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  version         = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  cluster_endpoint_public_access       = false     # 퍼블릭 차단
  cluster_endpoint_private_access      = true     # 프라이빗도 ON

  vpc_id     = data.terraform_remote_state.vpc.outputs.vpc_id
  subnet_ids = data.terraform_remote_state.vpc.outputs.private_subnet_ids

  enable_irsa = true

  eks_managed_node_groups = {
    service-nodes = {
      instance_types = ["t3.medium"]
      desired_size   = 2
      min_size       = 1
      max_size       = 3
    }
  }

  tags = {
    Name    = var.cluster_name
    Purpose = "msa-service"
  }
}
