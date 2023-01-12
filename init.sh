#!/usr/bin/env bash
set -e # Exit if error is detected during pipeline execution => terraform failing
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [[ -z "${API_DOMAIN}" ]]; then
  echo "API_DOMAIN env variable is not set. It should be set to either customized domain name or using a dummy name mydomain.com".
  exit
fi

if [[ -z "${PROJECT_ID}" ]]; then
  echo "PROJECT_ID variable is not set".
  exit
fi

source "${DIR}"/SET
gcloud config set project $PROJECT_ID

# Run following commands when executing from the local development machine (and not from Cloud Shell)
#gcloud auth login
#gcloud auth application-default login

export ORGANIZATION_ID=$(gcloud organizations list --format="value(name)")
export ADMIN_EMAIL=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
export TF_VAR_admin_email=${ADMIN_EMAIL}

# For Argolis Only
#gcloud resource-manager org-policies disable-enforce constraints/compute.requireOsLogin --organization=$ORGANIZATION_ID
#gcloud resource-manager org-policies delete constraints/compute.vmExternalIpAccess --organization=$ORGANIZATION_ID
#gcloud resource-manager org-policies delete constraints/compute.requireShieldedVm --organization=$ORGANIZATION_ID


bash "${DIR}"/setup/setup_terraform.sh

cd "${DIR}/terraform/environments/dev" || exit
terraform init -backend-config=bucket=$TF_BUCKET_NAME

terraform apply -target=module.project_services -target=module.service_accounts -auto-approve

terraform apply -auto-approve

# eventarc and ksa are always failing when running first time. Re-running apply command is an overcall (due re-building Cloud Run), but works
# terraform apply -target=module.gke -target=module.eventarc -auto-approve
#terraform apply -target=module.eventarc -auto-approve

bash ../../../setup/update_config.sh

gsutil cp "${DIR}/common/src/common/parser_config.json" "gs://${TF_VAR_config_bucket}/parser_config.json"

# TODO Add instructions on Cloud DNS Setup for API_DOMAIN

# Cloud DNS
# Enable Cloud DNS API
# https://docs.google.com/document/d/1oHpOwUfeIMKfe7b1UN7Vd1OoZzn9Gndxvmi-ANcxB_Q/preview?resourcekey=0-pAmIVo-ap-zCzd_HD-W5IQ
# gcloud dns --project=pa-document-ai managed-zones create pa-docai-demo --description="" --dns-name="evekhm.demo.altostrat.com." --visibility="public" --dnssec-state="off"

# REGISTRAR SETUP
#ns-cloud-e1.googledomains.com.
#ns-cloud-e2.googledomains.com.
#ns-cloud-e3.googledomains.com.
#ns-cloud-e4.googledomains.com.

# Submit a DNS delegation request

gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID

