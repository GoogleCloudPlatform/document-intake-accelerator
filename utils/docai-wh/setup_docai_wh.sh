#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

LOG="$DIR/deploy.log"
filename=$(basename $0)
timestamp=$(date +"%m-%d-%Y_%H:%M:%S")
echo "$timestamp - Running $filename ... " | tee "$LOG"

source "${DIR}/SET"

if [[ -z "${PROJECT_ID}" ]]; then
  echo PROJECT_ID env variable is not set.  | tee -a "$LOG"
  exit
fi

if [[ -z "${PROCESSOR_ID}" ]]; then
  echo PROCESSOR_ID env variable is not set.  | tee -a "$LOG"
  exit
fi

pip install -r requirements.txt  | tee -a "$LOG"

#gcloud auth application-default login

echo "Disabling Organization Policy preventing Service Account Key Creation.. " | tee -a "$LOG"
gcloud services enable orgpolicy.googleapis.com | tee -a "$LOG"

enabled=$(gcloud services list --enabled | grep orgpolicy)
while [ -z "$enabled" ]; do
  enabled=$(gcloud services list --enabled | grep orgpolicy)
  sleep 5;
done

gcloud org-policies reset constraints/iam.disableServiceAccountKeyCreation --project=$PROJECT_ID | tee -a "$LOG"

echo "Waiting for policy change to get propagated...."  | tee -a "$LOG"
sleep 30

if gcloud iam service-accounts list --project $PROJECT_ID | grep -q $SA_NAME; then
  echo "Service account $SA_NAME has been found." | tee -a "$LOG"
else
  echo "Creating Service Account ... "  | tee -a "$LOG"
  gcloud iam service-accounts create $SA_NAME \
          --description="Service Account for calling DocAI API and Document Warehouse API" \
          --display-name="docai-utility-sa"  | tee -a "$LOG"
fi



echo "Generating and Downloading Service Account key"  | tee -a "$LOG"
gcloud iam service-accounts keys create "${KEY_NAME}"  --iam-account=${SA_EMAIL} | tee -a "$LOG"


echo "Assigning required roles to ${SA_EMAIL}" | tee -a "$LOG"
gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/logging.logWriter" | tee -a "$LOG"

gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/storage.objectViewer" | tee -a "$LOG"


echo "Creating DocAI output bucket  ${DOCAI_OUTPUT_BUCKET}" | tee -a "$LOG"
gsutil ls "gs://${DOCAI_OUTPUT_BUCKET}" 2> /dev/null
RETURN=$?
if [[ $RETURN -gt 0 ]]; then
    echo "Bucket does not exist, creating gs://${DOCAI_OUTPUT_BUCKET}" | tee -a "$LOG"
    gsutil mb gs://"$DOCAI_OUTPUT_BUCKET" | tee -a "$LOG"
    gcloud storage buckets add-iam-policy-binding  gs://"$DOCAI_OUTPUT_BUCKET" --member="serviceAccount:${SA_EMAIL}" --role="roles/storage.admin" | tee -a "$LOG"
fi

echo "Adding required roles/permissions for ${SA_EMAIL} " | tee -a "$LOG"
gcloud projects add-iam-policy-binding $DOCAI_WH_PROJECT_ID --member="serviceAccount:${SA_EMAIL}"  --role="roles/documentai.apiUser" | tee -a "$LOG"
gcloud projects add-iam-policy-binding $DOCAI_WH_PROJECT_ID --member="serviceAccount:${SA_EMAIL}"  --role="roles/contentwarehouse.documentAdmin"  | tee -a "$LOG"
gcloud projects add-iam-policy-binding $DOCAI_WH_PROJECT_ID --member="serviceAccount:${SA_EMAIL}"  --role="roles/contentwarehouse.admin"  | tee -a "$LOG"
gcloud projects add-iam-policy-binding $DOCAI_WH_PROJECT_ID --member="serviceAccount:${SA_EMAIL}"  --role="roles/documentai.viewer"  | tee -a "$LOG"

# Give Access to DocAI service account to access input bucket
if [ "$DATA_PROJECT_ID" != "$DOCAI_WH_PROJECT_ID" ]; then
    gcloud projects add-iam-policy-binding "$DATA_PROJECT_ID" --member="serviceAccount:${SA_EMAIL}"  --role="roles/storage.objectViewer"  | tee -a "$LOG"
    gcloud projects add-iam-policy-binding "$DATA_PROJECT_ID" --member="serviceAccount:${SA_DOCAI}"  --role="roles/storage.objectViewer" | tee -a "$LOG"
    gcloud projects add-iam-policy-binding "$DATA_PROJECT_ID" --member="serviceAccount:${SA_DOCAI_WH}"  --role="roles/storage.objectViewer" | tee -a "$LOG"
fi

if [ "$DATA_PROJECT_ID" != "$DOCAI_PROJECT_ID" ]; then
    gcloud projects add-iam-policy-binding "$DATA_PROJECT_ID" --member="serviceAccount:${SA_DOCAI}"  --role="roles/storage.objectViewer" | tee -a "$LOG"
fi

if [ "$DOCAI_PROJECT_ID" != "$DOCAI_WH_PROJECT_ID" ]; then
  gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID --member="serviceAccount:${SA_EMAIL}"  --role="roles/documentai.viewer"  2>&1
  gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID --member="serviceAccount:${SA_EMAIL}"  --role="roles/documentai.apiUser"  2>&1
fi

timestamp=$(date +"%m-%d-%Y_%H:%M:%S")
echo "$timestamp Finished. Saved Log into $LOG"  | tee -a "$LOG"