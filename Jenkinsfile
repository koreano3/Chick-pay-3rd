pipeline {
  agent any

  triggers {
    githubPush()  // ⬅️ 이게 꼭 필요!
  }

  stages {
    stage('Test') {
      steps {
        echo '✅ GitHub webhook 트리거 성공!'
      }
    }
  }
}
