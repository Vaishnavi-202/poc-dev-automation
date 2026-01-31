pipeline {
    agent {
        label 'windows-pywinauto'   // same agent as previous project
    }

    environment {
        IMAGE_NAME = "ghcr.io/vaishnavi-202/poc-dev-automation:latest"
    }

    stages {

        stage('Login to GHCR') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'ghcr-creds',
                    usernameVariable: 'GHCR_USER',
                    passwordVariable: 'GHCR_TOKEN'
                )]) {
                    bat '''
                    echo %GHCR_TOKEN% | docker login ghcr.io -u %GHCR_USER% --password-stdin
                    '''
                }
            }
        }

        stage('Pull Docker Image') {
            steps {
                bat '''
                docker pull %IMAGE_NAME%
                '''
            }
        }

        stage('Run Automation Container') {
            steps {
                bat '''
                docker run --rm %IMAGE_NAME%
                '''
            }
        }
    }

    post {
        success {
            echo "Automation executed successfully"
        }
        failure {
            echo "Automation failed"
        }
    }
}
