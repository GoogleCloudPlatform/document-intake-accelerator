#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/SET
PWD=$(pwd)
export TF_VAR_admin_email=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
export TF_VAR_api_domain=$(kubectl describe ingress default-ingress | grep Address | awk '{print $2}')
export API_DOMAIN=$TF_VAR_api_domain
echo "Using IP address = $TF_VAR_api_domain"
cd terraform/environments/dev || exit
terraform apply -target=module.cloudrun-queue -target=module.cloudrun-start-pipeline
cd $PWD || exit