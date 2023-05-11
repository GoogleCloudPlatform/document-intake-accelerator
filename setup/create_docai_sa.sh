#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/../SET

if [ -z "$DOCAI_PROJECT_ID" ]; then
  echo "DOCAI_PROJECT_ID env variable must be set, exiting."
  exit
fi

if [ -z "$PROJECT_ID" ]; then
  echo "PROJECT_ID env variable must be set, exiting."
  exit
fi

# constraints/iam.disableServiceAccountKeyCreation

SA_NAME=cda-docai
SA_EMAIL=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

gcloud config set project $PROJECT_ID
gcloud iam service-accounts create $SA_NAME \
        --description="Doc AI invoker" \
        --display-name="cda docai invoker"

# DOCAI Access
gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/documentai.apiUser"
gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/documentai.editor"

gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/logging.viewer"

gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/storage.objectViewer"

 gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/editor"

export KEY=${PROJECT_ID}_${SA_NAME}.json
gcloud iam service-accounts keys create ${KEY} \
        --iam-account=${SA_EMAIL}

export GOOGLE_APPLICATION_CREDENTIALS=${KEY}