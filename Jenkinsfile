#!groovy
@Library('lts-basic-pipeline') _

// projName is the directory name for the project on the servers for it's docker/config files
// default values: 
//  registryCredentialsId = "${env.REGISTRY_ID}"
//  registryUri = 'https://registry.lts.harvard.edu'
def endpoints = []
ltsBasicPipeline.call("rabbitmq-email-notifier", "DAIS", "hdc3a", "10582", endpoints, "hdc-3a")
