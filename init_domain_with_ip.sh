#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/SET

gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID

export TF_VAR_admin_email=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")

export API_DOMAIN=$(kubectl describe ingress default-ingress | grep Address | awk '{print $2}')
export TF_VAR_api_domain=$API_DOMAIN

echo "Using IP address = $TF_VAR_api_domain"
cd terraform/environments/dev || exit
terraform apply -target=module.cloudrun-queue -target=module.cloudrun-start-pipeline -auto-approve
cd ../../../

