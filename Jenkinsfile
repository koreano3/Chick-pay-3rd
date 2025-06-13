pipeline {
    agent any

    environment {
        REGION = 'ap-northeast-2'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Git Diff') {
            steps {
                script {
                    changedFiles = sh(script: "git diff --name-only HEAD~1 HEAD", returnStdout: true).trim().split("\n")
                    changedDirs = changedFiles.collect {
                        if (it.startsWith("front-service/")) return "front-service"
                        else if (it.startsWith("user-service/")) return "user-service"
                        else if (it.startsWith("transaction-service/")) return "transaction-service"
                        else return null
                    }.findAll { it != null }.unique()
                    echo "변경된 서비스 디렉토리: ${changedDirs}"
                }
            }
        }

        stage('Docker Build & Push') {
            steps {
                script {
                    def services = [
                        'front-service': [
                            context: './front-service/react-app',
                            ecr: '297195401389.dkr.ecr.ap-northeast-2.amazonaws.com/zapp/react-app'
                        ],
                        'user-service': [
                            context: './user-service',
                            ecr: '297195401389.dkr.ecr.ap-northeast-2.amazonaws.com/zapp/user-service'
                        ],
                        'transaction-service': [
                            context: './transaction-service',
                            ecr: '297195401389.dkr.ecr.ap-northeast-2.amazonaws.com/zapp/transaction-service'
                        ]
                    ]

                    changedDirs.each { service ->
                        def config = services[service]
                        def imageName = "${config.ecr}:${IMAGE_TAG}"

                        echo "🔧 ${service} 변경 감지됨 -> 빌드: ${config.context}, 푸시: ${config.ecr}"
                        sh """
                            aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${config.ecr}
                            docker build -t ${imageName} ${config.context}
                            docker push ${imageName}
                        """
                    }
                }
            }
        }
    }
}
