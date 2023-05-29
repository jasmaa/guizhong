pipeline {
    agent any
    stages {
        stage('Clone source') {
            steps {
                git url: 'https://github.com/jasmaa/guizhong', branch: 'main'
            }
        }
    }
}