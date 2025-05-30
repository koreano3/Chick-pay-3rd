pipeline {
  agent any

  triggers {
    githubPush()  // 🔔 GitHub webhook push 이벤트로 트리거
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

    stage('Terraform Init') {
      steps {
        dir('infra/terraform') {
          sh 'terraform init'
        }
      }
    }

    stage('Terraform Plan') {
      steps {
        dir('infra/terraform') {
          sh 'terraform plan -out=tfplan'
        }
      }
    }

    stage('Terraform Apply') {
      steps {
        input message: '✅ Terraform apply 실행할까요?'
        dir('infra/terraform') {
          sh 'terraform apply -auto-approve tfplan'
        }
      }
    }
  }

  post {
    success {
      echo '✅ Terraform 파이프라인 정상 완료!'
    }
    failure {
      echo '❌ 실패: Jenkins Console Output 확인 요망'
    }
  }
}
