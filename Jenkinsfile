pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }
    stages {
        // Run the build in the against the dev branch to check for compile errors
        stage('Add CLA label to PR') {
            environment {
                //spawns GITHUB_USR and GITHUB_PSW environment variables
                GITHUB=credentials('38b2e4a6-167a-40b2-be6f-d69be42c8190')
            }
            steps {
                // Using an install of Github repo CLA tagger
                // (https://github.com/forslund/github-repo-cla)
                sh '~/github-repo-cla/mycroft-core-cla-check.sh'
            }
        }
    }
}
