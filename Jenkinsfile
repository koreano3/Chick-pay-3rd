pipeline {
    agent any

    environment {
        REGION = 'ap-northeast-2'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "📥 Git 소스코드 체크아웃"
                checkout scm  // 🔥 Git 명령 쓰기 전 필수!
            }
        }

        stage('Git Diff 분석') {
            steps {
                script {
                    echo "🔍 변경 파일 확인"
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

        stage('Docker Build & Push to ECR') {
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

                    if (changedDirs.isEmpty()) {
                        echo "변경된 서비스 없음. 아무것도 빌드하지 않습니다."
                    } else {
                        changedDirs.each { service ->
                            def config = services[service]
                            def imageName = "${config.ecr}:${IMAGE_TAG}"

                            echo "🚀 [${service}] 빌드 시작 (경로: ${config.context}) → ECR: ${config.ecr}"
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
}
