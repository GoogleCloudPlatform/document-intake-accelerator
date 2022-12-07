#!/usr/bin/env bash
#set -e # Exit if error is detected during pipeline execution => terraform failing
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/SET
gcloud config set project $PROJECT_ID
gcloud auth login
gcloud auth application-default login

export ORGANIZATION_ID=$(gcloud organizations list --format="value(name)")
export ADMIN_EMAIL=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
export TF_VAR_admin_email=${ADMIN_EMAIL}

# For Argolis Only
#gcloud resource-manager org-policies disable-enforce constraints/compute.requireOsLogin --organization=$ORGANIZATION_ID
#gcloud resource-manager org-policies delete constraints/compute.vmExternalIpAccess --organization=$ORGANIZATION_ID


bash "${DIR}"/setup/setup_terraform.sh

cd "${DIR}/terraform/environments/dev" || exit
terraform init -backend-config=bucket=$TF_BUCKET_NAME

terraform apply -target=module.project_services -target=module.service_accounts -auto-approve
sleep 40
terraform apply  -auto-approve

# eventarc and ksa are always failing when running first time. Re-running apply command is an overcall (due re-building Cloud Run), but works
# terraform apply -target=module.gke -target=module.eventarc -auto-approve
terraform apply  -auto-approve

bash ../../../setup/update_config.sh

gsutil cp "${DIR}/common/src/common/parser_config.json" "gs://${PROJECT_ID}/config/parser_config.json"
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

