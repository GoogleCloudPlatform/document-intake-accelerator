#!/usr/bin/env bash
export DISPLAY_NAME="cda-ui"
export USER_EMAIL=$(gcloud config list account --format "value(core.account)")
export IAP_SECRET_NAME=cda-iap
export SA_START_PIPELINE="cloudrun-startpipeline-sa@${PROJECT_ID}.iam.gserviceaccount.com"
export SA_QUEUE="cloudrun-queue-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Configuring the OAuth consent screen
gcloud alpha iap oauth-brands create \
    --application_title="CDA Application" \
    --support_email=$USER_EMAIL

# Creating an IAP OAuth Client
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='get(projectNumber)')
gcloud alpha iap oauth-clients create \
    projects/$PROJECT_ID/brands/$PROJECT_NUMBER \
    --display_name=$DISPLAY_NAME

export CLIENT_NAME=$(gcloud alpha iap oauth-clients list \
    projects/$PROJECT_NUMBER/brands/$PROJECT_NUMBER --format='value(name)' \
    --filter="displayName:$DISPLAY_NAME")

export CLIENT_ID=${CLIENT_NAME##*/}

export CLIENT_SECRET=$(gcloud alpha iap oauth-clients describe $CLIENT_NAME --format='value(secret)')

echo "Generated CLIENT_ID=$CLIENT_ID CLIENT_SECRET=$CLIENT_SECRET"

if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
  echo "CLIENT_ID and CLIENT_SECRET are not be set"
  exit
fi

echo "Creating GKE Secret"
kubectl create secret generic $IAP_SECRET_NAME \
   --from-literal=client_id=$CLIENT_ID \
   --from-literal=client_secret=$CLIENT_SECRET


function add_user(){
  USER=$1
  if  [ -n "${USER}" ]; then
    gcloud iap web add-iam-policy-binding \
      --resource-type=backend-services \
      --service="$validation_be" \
      --member=user:$USER \
      --role='roles/iap.httpsResourceAccessor'
  fi
}
function enable_iap(){
  service_name=$1
  validation_be=$(gcloud compute backend-services list --format='get(NAME)' | grep $service_name)
  echo "service=$service_name backend=$validation_be"
  if [ -n "$validation_be" ]; then
    gcloud iap web enable --resource-type=backend-services \
        --oauth2-client-id=$CLIENT_ID \
        --oauth2-client-secret=$CLIENT_SECRET \
        --service="$validation_be"
  fi
  add_user "${USER_EMAIL}"
  add_user "${SA_START_PIPELINE}"
  add_user "${SA_QUEUE}"

}

enable_iap validation-service
enable_iap upload-service
enable_iap matching-service
enable_iap hitl-service
enable_iap extraction-service
enable_iap document-status-service
enable_iap config-service
enable_iap classification-service


#TODO Add User Group to IAP for real life scenario



