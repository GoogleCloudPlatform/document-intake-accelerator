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

declare -a EnvVars=(
  "PROJECT_ID"
  "ADMIN_EMAIL"
  "TF_BUCKET_NAME"
  "TF_BUCKET_LOCATION"
)
for variable in ${EnvVars[@]}; do
  if [[ -z "${!variable}" ]]; then
    input_value=""
    while [[ -z "$input_value" ]]; do
      read -p "Enter the value for ${variable}: " input_value
      declare "${variable}=$input_value"
    done
  fi
done

BLUE=$(tput setaf 4)
RED=$(tput setaf 1)
NORMAL=$(tput sgr0)

create_bucket () {
  printf "PROJECT_ID=${PROJECT_ID}\n"
  printf "TF_BUCKET_NAME=${TF_BUCKET_NAME}\n"
  printf "TF_BUCKET_LOCATION=${TF_BUCKET_LOCATION}\n"
  
  print_highlight "Creating terraform state bucket: ${TF_BUCKET_NAME}\n"
  gsutil mb -l $TF_BUCKET_LOCATION gs://$TF_BUCKET_NAME
  gsutil versioning set on gs://$TF_BUCKET_NAME
  export TF_BUCKET_NAME=$TF_BUCKET_NAME
  echo
}

enable_apis () {
  gcloud services enable iamcredentials.googleapis.com
}

create_sa () {
  declare -a roles=(
    "roles/aiplatform.admin"
    "roles/artifactregistry.admin"
    "roles/cloudbuild.builds.builder"
    "roles/cloudtrace.agent"
    "roles/compute.admin"
    "roles/container.admin"
    "roles/containerregistry.ServiceAgent"
    "roles/datastore.owner"
    "roles/eventarc.admin"
    "roles/eventarc.eventReceiver"
    "roles/eventarc.serviceAgent"
    "roles/firebase.admin"
    "roles/iam.serviceAccountTokenCreator"
    "roles/iam.serviceAccountUser"
    "roles/iam.workloadIdentityUser"
    "roles/logging.admin"
    "roles/logging.viewer"
    "roles/run.admin"
    "roles/run.invoker"
    "roles/secretmanager.secretAccessor"
    "roles/storage.admin"
    "roles/viewer"
  )
  service_account_name="terraform-sa"
  
  printf "Creating Terraform Service Account: ${service_account_name}@${PROJECT_ID}.iam.gserviceaccount.com"
  gcloud iam service-accounts create ${service_account_name} \
  --description="Terraform SA" \
  --display-name="${service_account_name}"
  
  for role in ${roles[@]}; do
    printf "Binding role ${role} to TF service account..."
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${service_account_name}@${PROJECT_ID}.iam.gserviceaccount.com" --role="${role}"
  done
  
  gcloud iam service-accounts add-iam-policy-binding \
  ${service_account_name}@${PROJECT_ID}.iam.gserviceaccount.com \
  --member="user:${ADMIN_EMAIL}" \
  --role="roles/iam.serviceAccountUser"
}

print_highlight () {
  printf "${BLUE}$1${NORMAL}\n"
}

create_bucket
enable_apis
# create_sa

print_highlight "Terraform state bucket: ${TF_BUCKET_NAME}\n"
