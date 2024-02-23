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

LOG="$DIR/init_gke.log"
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

cd "${DIR}/terraform/stages/gke-ingress" || exit

gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID

terraform init -backend-config=bucket="$TF_BUCKET_NAME" -upgrade  2>&1 | tee -a "$LOG"
terraform apply -auto-approve  2>&1 | tee -a "$LOG"


cd "$PWD" || exit

timestamp=$(date +"%m-%d-%Y_%H:%M:%S")
echo "$timestamp Completed! Saved Log into $LOG" | tee -a "$LOG"



