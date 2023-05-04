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
source "${DIR}/../SET"

if [ -z "$PROJECT_ID" ]; then
  echo "PROJECT_ID is not set, quitting..."
  exit
fi

if [ -z "$DOCAI_PROJECT_ID" ]; then
  echo "DOCAI_PROJECT_ID is not set, quitting..."
  exit
fi


if [ "$DOCAI_PROJECT_ID" != "$PROJECT_ID" ]; then
  echo "Assigning Cross Project Access"
  gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID --member="serviceAccount:gke-sa@${PROJECT_ID}.iam.gserviceaccount.com"  --role="roles/documentai.viewer"  2>&1
  PROJECT_DOCAI_NUMBER=$(gcloud projects describe "$DOCAI_PROJECT_ID" --format='get(projectNumber)')
  SA_DOCAI="service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com"
  gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-docai-output --member="serviceAccount:$SA_DOCAI" --role="roles/storage.admin"  2>&1
  gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-document-upload --member="serviceAccount:$SA_DOCAI" --role="roles/storage.objectViewer"  2>&1
  #gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_DOCAI"  --role="roles/storage.admin"  2>&1

  #echo "Validating Assigned Roles:"
  #gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --format='table(bindings.role)' --filter="bindings.members:${SA_DOCAI}"
fi