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

GSA_NAME="claims-processing-dev-sa"
KSA_NAME="ksa"

declare EXISTING_KSA=`kubectl get sa -n ${NAMESPACE} | egrep -i "^${KSA_NAME} "`
if [[ "$EXISTING_KSA" = "" ]]; then
  kubectl create serviceaccount -n ${NAMESPACE} ${KSA_NAME}
fi

gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${GCP_PROJECT}.svc.id.goog[${NAMESPACE}/${KSA_NAME}]" \
  ${GSA_NAME}@${GCP_PROJECT}.iam.gserviceaccount.com

kubectl annotate serviceaccount \
  --overwrite \
  --namespace ${NAMESPACE} \
  ${KSA_NAME} \
  iam.gke.io/gcp-service-account=${GSA_NAME}@${GCP_PROJECT}.iam.gserviceaccount.com