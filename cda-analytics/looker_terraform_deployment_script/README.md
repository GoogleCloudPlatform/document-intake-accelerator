# Setup Development Environment

### Install Terraform
```
$ cd ~
$ curl https://releases.hashicorp.com/terraform/1.3.4/terraform_1.3.4_linux_amd64.zip -o terraform.zip
$ unzip terraform.zip
$ sudo mv terraform /usr/local/bin
$ terraform version
```

### Install and Configure GCloud SDK
```
$ sudo apt update
$ sudo apt install -y google-cloud-sdk
$ gcloud auth login <your email address> --no-launch-browser
$ gcloud auth application-default login --no-launch-browser
```

### Install Docker
For Specific OS Refer: https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script

Below is example for installing Docker on Debian:
```
$ curl -fsSL https://get.docker.com -o get-docker.sh
$ sudo sh ./get-docker.sh
```

### Install Kubectl
Reference: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
```
$ sudo apt install -y kubectl
$ sudo apt install -y google-cloud-sdk-gke-gcloud-auth-plugin
```

### Install helm
Reference: https://helm.sh/docs/intro/install/
```
$ curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
$ chmod 700 get_helm.sh
$ ./get_helm.sh
```

### Clone Git Repository
```
$ git clone [https://github.com/hcls-solutions/hde-accelerators](https://github.com/hcls-solutions/claims-data-activator/edit/main/cda-analytics).git
```
