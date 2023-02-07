#!/usr/bin/env bash
set -e # Exit if error is detected during pipeline execution
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/SET

if [[ -z "${API_DOMAIN}" ]]; then
  echo API_DOMAIN env variable is not set. Using External Ingress IP address...
  export API_DOMAIN=$(kubectl describe ingress default-ingress | grep Address | awk '{print $2}')
  echo API_DOMAIN="$API_DOMAIN"
fi

if [[ -z "${PROJECT_ID}" ]]; then
  echo PROJECT_ID variable is not set.
  exit
fi

source "${DIR}"/microservices/adp_ui/.env  # to get settings into config map, to be able to retrieve them later on when re-deploying
gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID
skaffold run  -p prod --default-repo=gcr.io/${PROJECT_ID}

#TODO terraform to re-deploy cloud-run instead
#bash "$DIR"/cloudrun/startpipeline/deploy.sh
#bash "$DIR"/cloudrun/queue/deploy.sh

#PYTHONPATH=$BASE_DIR/common/src python microservices/extraction_service/src/main.py