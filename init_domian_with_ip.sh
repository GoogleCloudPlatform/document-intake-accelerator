#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/SET
PWD=$(pwd)
export TF_VAR_admin_email=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
export API_DOMAIN=$(kubectl describe ingress | grep Address | awk '{print $2}')
echo "Using IP address = $API_DOMAIN"
export TF_VAR_api_domain=$API_DOMAIN
cd terraform/environments/dev || exit
terraform apply -target=module.cloudrun
cd $PWD || exit