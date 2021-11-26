// vim: set filetype=groovy:

def image_local_name = "imagetagger"
def image_base_name = "ghcr.io/bit-bots/imagetagger"

pipeline {
    agent {
        kubernetes {
            yaml """
kind: Pod
spec:
  containers:
    - name: kustomize
      image: docker.io/nekottyo/kustomize-kubeval
      tty: true
      command:
        - cat
    - name: podman
      image: quay.io/podman/stable
      tty: true
      securityContext:
        privileged: true
      command:
        - cat
"""
        }
    }
    options {
        skipDefaultCheckout(true)
    }
    stages {
        stage("Checkout SCM") {
            steps {
                checkout scm
            }
        }
        stage("Check Kubernetes config validity") {
            steps {
                container("kustomize") {
                    gitStatusWrapper(
                        credentialsId: "github-credentials",
                        description: "Check Kubernetes config validity",
                        failureDescription: "Kubernetes config is not valid",
                        successDescription: "Kubernetes config is valid",
                        gitHubContext: "check-k8s"
                    ) {
                        sh "kustomize build . > k8s.yml"
                        sh "kubeval k8s.yml --strict"
                    }
                }
            }
        }
        stage("Build Container Image") {
            steps {
                container("podman") {
                    gitStatusWrapper(
                        credentialsId: "github-credentials",
                        description: "Build the container image",
                        failureDescription: "Container image failed to build",
                        successDescription: "Container image was successfully built",
                        gitHubContext: "build-container-image"
                    ) {
                        sh "podman build -t ${image_local_name} ."
                    }
                }
            }
        }
        stage("Upload Container Image") {
            steps {
                container("podman") {
                    gitStatusWrapper(
                        credentialsId: "github-credentials",
                        description: "Upload the container image",
                        failureDescription: "Could not upload the container image",
                        successDescription: "Container upload was successful or skipped",
                        gitHubContext: "upload-container-image"
                    ) {
                        milestone(ordinal: 100)

                        script {
                            withCredentials([usernamePassword(
                                credentialsId: 'github-credentials',
                                passwordVariable: 'registry_password',
                                usernameVariable: 'registry_username'
                            )]) {
                                if (env.TAG_NAME != null) {
                                    // tag events get pushed as the corresponding tag
                                    sh "podman login ghcr.io -u $registry_username -p $registry_password"
                                    sh "podman tag ${image_local_name} ${image_base_name}:${env.TAG_NAME}"
                                    sh "podman push ${image_base_name}:${env.TAG_NAME}"
                                }

                                if (env.BRANCH_IS_PRIMARY == "true") {
                                    // commit events get pushed as :dev-latest
                                    sh "podman login ghcr.io -u $registry_username -p $registry_password"
                                    sh "podman tag ${image_local_name} ${image_base_name}:dev-latest"
                                    sh "podman push ${image_base_name}:dev-latest"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
