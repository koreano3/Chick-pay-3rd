pipeline {
  agent any

  triggers {
    githubPush()  // 🔔 GitHub Webhook 트리거
  }

  environment {
    TF_IN_AUTOMATION = 'true'
    AWS_REGION       = 'ap-northeast-2'
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'cicd', url: 'https://github.com/bemajor-team/Chick-pay-3rd.git'
      }
    }

    stage('Terraform VPC') {
      steps {
        dir('infra/terraform/vpc') {
          sh 'terraform init'
          sh 'terraform plan -out=tfplan'
          input message: '🌐 VPC apply 실행할까요?'
          sh 'terraform apply -auto-approve tfplan'
        }
      }
    }

    stage('Terraform IAM') {
      steps {
        dir('infra/terraform/iam') {
          sh 'terraform init'
          sh 'terraform plan -out=tfplan'
          input message: '🔐 IAM apply 실행할까요?'
          sh 'terraform apply -auto-approve tfplan'
        }
      }
    }

    stage('Terraform EKS CICD') {
      steps {
        dir('infra/terraform/eks/cicd') {
          sh 'terraform init'
          sh 'terraform plan -out=tfplan'
          input message: '🚀 EKS CICD apply 실행할까요?'
          sh 'terraform apply -auto-approve tfplan'
        }
      }
    }

    stage('Terraform EKS Service') {
      steps {
        dir('infra/terraform/eks/service') {
          sh 'terraform init'
          sh 'terraform plan -out=tfplan'
          input message: '📦 EKS Service apply 실행할까요?'
          sh 'terraform apply -auto-approve tfplan'
        }
      }
    }

    stage('Terraform Helm') {
      steps {
        dir('infra/terraform/helm') {
          sh 'terraform init'
          sh 'terraform plan -out=tfplan'
          input message: '🧩 Helm 모듈 apply 실행할까요?'
          sh 'terraform apply -auto-approve tfplan'
        }
      }
    }
  }

  post {
    success {
      echo '✅ Terraform 파이프라인이 정상 완료되었습니다!'
    }
    failure {
      echo '❌ 파이프라인 실패: Jenkins Console Output을 확인해주세요.'
    }
  }
}
