pipeline {
  agent any

  triggers {
    githubPush()
  }

  stages {
    stage('Build') {
      steps {
        echo 'GitHub 푸시로 트리거된 빌드!'
      }
    }
  }
}
