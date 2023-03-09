#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

LOG="$DIR/deploy.log"
filename=$(basename $0)
timestamp=$(date +"%m-%d-%Y_%H:%M:%S")
echo "$timestamp - Running $filename ... " | tee "$LOG"

source "${DIR}"/SET

if [[ -z "${API_DOMAIN}" ]]; then
  echo API_DOMAIN env variable is not set. Using External Ingress IP address... | tee -a "$LOG"
  export API_DOMAIN=$(kubectl describe ingress default-ingress | grep Address | awk '{print $2}')
  echo API_DOMAIN="$API_DOMAIN"| tee -a "$LOG"
fi

if [[ -z "${PROJECT_ID}" ]]; then
  echo PROJECT_ID variable is not set. | tee -a "$LOG"
  exit
fi

# Only first time copy to GCS .env, next when re-deploying, retrieve back those variables.
ENV_CONFIG="gs://${TF_VAR_config_bucket}/adp_ui.env"
gsutil -q stat "$ENV_CONFIG" 2> /dev/null | tee -a "$LOG"
RETURN=$?
if [[ $RETURN -gt 0 ]]; then
    echo "UI config does not exist in gs://${TF_VAR_config_bucket}/.env" | tee -a "$LOG"
    echo "Copying frontend settings to GCS as a safe backup storage..." | tee -a "$LOG"
    gsutil cp "${DIR}/microservices/adp_ui/.env" "$ENV_CONFIG" | tee -a "$LOG"
else
  echo "Retrieving frontend config from GCS backup:" | tee -a "$LOG"
  gsutil cp "$ENV_CONFIG" "${DIR}/microservices/adp_ui/.env" | tee -a "$LOG"
fi


gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID
skaffold run -p prod --default-repo=gcr.io/${PROJECT_ID} | tee -a "$LOG"

#TODO terraform to re-deploy cloud-run instead
#bash "$DIR"/cloudrun/startpipeline/deploy.sh
#bash "$DIR"/cloudrun/queue/deploy.sh

#PYTHONPATH=$BASE_DIR/common/src python microservices/extraction_service/src/main.py
timestamp=$(date +"%m-%d-%Y_%H:%M:%S")
echo "$timestamp Finished. Saved Log into $LOG"  | tee -a "$LOG"