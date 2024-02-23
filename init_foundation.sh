#!/bin/bash
# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e # Exit if error is detected during pipeline execution => terraform failing
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PWD=$(pwd)

LOG="$DIR/init_foundation.log"
filename=$(basename $0)
timestamp=$(date +"%m-%d-%Y_%H:%M:%S")

echo "$timestamp - Running $filename ... " | tee "$LOG"

if [[ -z "${API_DOMAIN}" ]]; then
  echo "API_DOMAIN env variable is not set.". | tee -a "$LOG"
  exit
fi

if [[ -z "${PROJECT_ID}" ]]; then
  echo "PROJECT_ID variable is not set". | tee -a "$LOG"
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

#FILE="${DIR}/terraform/environments/dev/terraform.tfvars"
#if test -f "$FILE"; then
#    :
#else
#  echo "Creating default terraform.tfvars ..."
#  cp "${DIR}/terraform/environments/dev/terraform.sample.tfvars" "${DIR}/terraform/environments/dev/terraform.tfvars"
#fi

bash "${DIR}"/setup/setup_terraform.sh  2>&1 | tee -a "$LOG"

cd "${DIR}/terraform/stages/foundation" || exit

terraform init -backend-config=bucket="$TF_BUCKET_NAME" -upgrade  2>&1 | tee -a "$LOG"
terraform apply -target=module.project_services -target=module.service_accounts -target=module.project_services_docai -auto-approve  2>&1 | tee -a "$LOG"
terraform apply -auto-approve  2>&1 | tee -a "$LOG"


# Constructing the Global Config File
bash ../../../setup/update_config.sh  2>&1 | tee -a "$LOG"

# Modify ACK deadline for the eventarc subscription (this could not be done via terraform API)
subscription=$(terraform output -json eventarc_subscription)
subscription_name=$(echo "$subscription" | tr -d '"' | sed 's:.*/::')
gcloud alpha pubsub subscriptions update "$subscription_name" --ack-deadline=120 --project $PROJECT_ID
subscription=$(terraform output -json queue_subscription)
subscription_name=$(echo "$subscription" | tr -d '"' | sed 's:.*/::')
gcloud alpha pubsub subscriptions update "$subscription_name" --ack-deadline=120 --project $PROJECT_ID

#TODO fix in TF to perform this step
if [ -n "$DOCAI_PROJECT_ID"  ] && [ "$DOCAI_PROJECT_ID" != "$PROJECT_ID" ]; then
  gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID --member="serviceAccount:gke-sa@${PROJECT_ID}.iam.gserviceaccount.com"  --role="roles/documentai.viewer"  2>&1 | tee -a "$LOG"
  PROJECT_DOCAI_NUMBER=$(gcloud projects describe "$DOCAI_PROJECT_ID" --format='get(projectNumber)')
  gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-docai-output --member="serviceAccount:service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com" --role="roles/storage.admin"  2>&1 | tee -a "$LOG"
  gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-document-upload --member="serviceAccount:service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com" --role="roles/storage.objectViewer"  2>&1 | tee -a "$LOG"
fi


gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID

cda_external_ui=$(terraform output -json cda_external_ui | python -m json.tool)
if [ "$cda_external_ui" = "true" ]; then
  echo "Applying backend config for external ingress.."
  kubectl apply -f "$DIR"/iap/k8s/backend-config.yaml
else
  echo "Applying backend config for internal ingress.."
  kubectl apply -f "$DIR"/iap/k8s/backend-config_internal.yaml
fi


#DocAI Warehouse integration - commenting out
#if [ -n "$DOCAI_WH_PROJECT_ID" ]; then
#  echo "Adding required roles/permissions for ${SERVICE_ACCOUNT_EMAIL_GKE} " | tee -a "$LOG"
#  gcloud projects add-iam-policy-binding $DOCAI_WH_PROJECT_ID --project=$PROJECT_ID  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL_GKE}"  --role="roles/contentwarehouse.documentAdmin"  | tee -a "$LOG"
#  gcloud projects add-iam-policy-binding $DOCAI_WH_PROJECT_ID --project=$PROJECT_ID --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL_GKE}"  --role="roles/contentwarehouse.admin"  | tee -a "$LOG"
#  gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA_DOCAI_WH}"  --role="roles/storage.objectViewer" | tee -a "$LOG"
#fi

cd "$PWD" || exit

timestamp=$(date +"%m-%d-%Y_%H:%M:%S")
echo "$timestamp Completed! Saved Log into $LOG" | tee -a "$LOG"



