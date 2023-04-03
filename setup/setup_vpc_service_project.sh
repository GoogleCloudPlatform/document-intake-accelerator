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

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/../SET

gcloud services enable vpcaccess.googleapis.com --project $PROJECT_ID
gcloud services enable container.googleapis.com --project $PROJECT_ID
gcloud services enable container.googleapis.com --project $HOST_PROJECT_ID

gcloud compute shared-vpc associated-projects add $PROJECT_ID \
    --host-project $HOST_PROJECT_ID

SERVICE_PROJECT_NUM=$(gcloud projects describe "$PROJECT_ID" --format='get(projectNumber)')

gcloud projects add-iam-policy-binding $HOST_PROJECT_ID \
    --member serviceAccount:service-$SERVICE_PROJECT_NUM@container-engine-robot.iam.gserviceaccount.com \
    --role=roles/container.hostServiceAgentUser
gcloud projects add-iam-policy-binding $HOST_PROJECT_ID \
    --member=serviceAccount:service-$SERVICE_PROJECT_NUM@container-engine-robot.iam.gserviceaccount.com \
    --role=roles/compute.securityAdmin
gcloud projects add-iam-policy-binding $HOST_PROJECT_ID \
    --member=serviceAccount:service-$SERVICE_PROJECT_NUM@container-engine-robot.iam.gserviceaccount.com \
    --role=roles/compute.networkUser
gcloud projects add-iam-policy-binding $HOST_PROJECT_ID \
    --member=serviceAccount:$SERVICE_PROJECT_NUM@cloudservices.gserviceaccount.com \
    --role=roles/compute.networkUser

# Set IAm Policy for created subnets
function set_subnet_policy(){
  SUBNET=$1
  ETAG=$(gcloud compute networks subnets get-iam-policy $SUBNET  --project $HOST_PROJECT_ID  --region $REGION --format="value(etag)")
  echo
  sed 's|SERVICE_PROJECT_NUM|'"$SERVICE_PROJECT_NUM"'|g; s|ETAG|'"$ETAG"'|g; ' setup/subnet-policy.yaml > setup/"${SUBNET}"-policy.yaml
  sed 's|PROJECT_ID|'"$PROJECT_ID"'|g; s|API_DOMAIN|'"$API_DOMAIN"'|g; ' microservices/adp_ui/.sample.env > microservices/adp_ui/.env

  cat setup/"${SUBNET}"-policy.yaml
  echo ""
  gcloud compute networks subnets set-iam-policy $SUBNET \
      setup/"${SUBNET}"-policy.yaml \
      --project $HOST_PROJECT_ID \
      --region $REGION
}

set_subnet_policy $SUBNET1
set_subnet_policy $SUBNET2

gcloud projects add-iam-policy-binding $HOST_PROJECT_ID \
--role "roles/compute.networkUser" \
--member "serviceAccount:service-$SERVICE_PROJECT_NUM@gcp-sa-vpcaccess.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $HOST_PROJECT_ID \
--role "roles/compute.networkUser" \
--member "serviceAccount:$SERVICE_PROJECT_NUM@cloudservices.gserviceaccount.com"

gcloud container subnets list-usable \
    --project $PROJECT_ID \
    --network-project $HOST_PROJECT_ID