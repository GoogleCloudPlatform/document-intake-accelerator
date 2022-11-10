DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/SET

gcloud config set project $PROJECT_ID
gcloud auth login
gcloud auth application-default login


export ORGANIZATION_ID=$(gcloud organizations list --format="value(name)")
gcloud resource-manager org-policies disable-enforce constraints/compute.requireOsLogin --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/compute.vmExternalIpAccess --organization=$ORGANIZATION_ID
#


bash "${DIR}"/setup/setup_terraform.sh

export GOOGLE_IMPERSONATE_SERVICE_ACCOUNT=terraform-sa@$PROJECT_ID.iam.gserviceaccount.com

exit

cd "${DIR}/terraform/environments/dev" || exit
terraform init
terraform apply

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