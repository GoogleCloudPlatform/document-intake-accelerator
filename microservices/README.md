# How to build and deploy microservices
This folder contains the code for all the microservices. You can build and deploy microservices to your GCP Project using the following steps:

## Prerequisites

1. Check the version of kustomize. We need version 4.5.7
```
kustomize version
```

2. Skip this step is your currently installed version is 
4.5.7. You can install kustomize by running the following 
commands
```
sudo rm /usr/local/bin/kustomize

curl -Lo install_kustomize "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" 
&& chmod +x install_kustomize

sudo ./install_kustomize 4.5.7 /usr/local/bin

kustomize version
```

3. Run the following commands to set the environment 
variables. Change the value of Project ID and API Domain for your environment:
```
export PROJECT_ID={Your GCP Project ID}
# e.g. export PROJECT_ID=cda-001-engine

export API_DOMAIN={Your API Domain}
# e.g. export API_DOMAIN=cda-001.com

source ../../SET
```

4. Authenticate to GCP
```
gcloud auth application-default login

gcloud auth login
```

5. Fetch K8 cluster endpoint and auth data by running the 
following command
```
gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID
```

## Build and deploy microservice
1. Change the directory to the microservice you want to build and deploy and use skaffold run to build and deploy the microservice code from the directory.
```
cd {Directory}
# e.g. cd hitl_service

skaffold run -p prod --default-repo=gcr.io/${PROJECT_ID}
```
