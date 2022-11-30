#!/usr/bin/env bash
set -e # Exit if error is detected during pipeline execution
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/SET
gcloud config set project $PROJECT_ID
#gcloud auth login
#gcloud auth application-default login

export ORGANIZATION_ID=$(gcloud organizations list --format="value(name)")

# For Argolis Only
gcloud resource-manager org-policies disable-enforce constraints/compute.requireOsLogin --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/compute.vmExternalIpAccess --organization=$ORGANIZATION_ID


bash "${DIR}"/setup/setup_terraform.sh

cd "${DIR}/terraform/environments/dev" || exit
terraform init -backend-config=bucket=$TF_BUCKET_NAME

terraform apply -target=module.project_services -target=module.service_accounts -auto-approve

terraform apply

bash ../../../setup/update_config.sh

BUCKET="gs://${PROJECT_ID}"
gsutil cp "${DIR}"/common/src/common/parser_config.json ${BUCKET}/config/parser_config.json
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

