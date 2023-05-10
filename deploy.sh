#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

LOG="$DIR/deploy.log"
filename=$(basename $0)
timestamp=$(date +"%m-%d-%Y_%H:%M:%S")
echo "$timestamp - Running $filename ... " | tee "$LOG"

source "${DIR}"/SET

if [[ -z "${API_DOMAIN}" ]]; then
  echo API_DOMAIN env variable is not set.  | tee -a "$LOG"
  exit
#  export API_DOMAIN=$(kubectl describe ingress default-ingress | grep Address | awk '{print $2}')
#  echo API_DOMAIN="$API_DOMAIN"| tee -a "$LOG"
fi

if [[ -z "${PROJECT_ID}" ]]; then
  echo PROJECT_ID variable is not set. | tee -a "$LOG"
  exit
fi

gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID


#Copy .env file to GCS for tracking changes
gsutil cp "${DIR}/microservices/adp_ui/.env" "gs://${TF_VAR_config_bucket}/.env" | tee -a "$LOG"

## Only first time copy to GCS .env, next when re-deploying, retrieve back those variables.
#ENV_CONFIG="gs://${TF_VAR_config_bucket}/.env"
#gsutil -q stat "$ENV_CONFIG" 2> /dev/null | tee -a "$LOG"
#RETURN=$?
#if [[ $RETURN -gt 0 ]]; then
#    echo "UI config does not exist in gs://${TF_VAR_config_bucket}/.env" | tee -a "$LOG"
#    echo "Copying frontend settings to GCS as a safe backup storage..." | tee -a "$LOG"
#    gsutil cp "${DIR}/microservices/adp_ui/.env" "$ENV_CONFIG" | tee -a "$LOG"
#else
#  echo "Retrieving frontend config from GCS backup:" | tee -a "$LOG"
#  gsutil cp "$ENV_CONFIG" "${DIR}/microservices/adp_ui/.env" | tee -a "$LOG"
#fi

kubectl apply -f "$DIR"/iap/k8s/backend-config.yaml

VERSION=$(kustomize version)
if [[ "$VERSION" != *"v4.5.7"* ]]; then
  sudo rm /usr/local/bin/kustomize
  curl -Lo install_kustomize "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" && chmod +x install_kustomize
  sudo ./install_kustomize 4.5.7 /usr/local/bin
  kustomize version
fi



skaffold run -p prod --default-repo=gcr.io/${PROJECT_ID} | tee -a "$LOG"


# Deploy CloudRUn and skip building of common (done previous steps)
#TODO terraform to re-deploy cloud-run instead
#bash "$DIR"/cloudrun/startpipeline/deploy.sh -s
#bash "$DIR"/cloudrun/queue/deploy.sh -s

#PYTHONPATH=$BASE_DIR/common/src python microservices/extraction_service/src/main.py
timestamp=$(date +"%m-%d-%Y_%H:%M:%S")
echo "$timestamp Finished. Saved Log into $LOG"  | tee -a "$LOG"