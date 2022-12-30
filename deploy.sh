#!/usr/bin/env bash
set -e # Exit if error is detected during pipeline execution
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/SET

if [[ -z "${API_DOMAIN}" ]]; then
  echo API_DOMAIN env variable is not set. It should be set to either External Ingress IP address or the customized domain name.
  exit
fi

if [[ -z "${PROJECT_ID}" ]]; then
  echo PROJECT_ID variable is not set.
  exit
fi

gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID
skaffold run  -p dev --default-repo=gcr.io/${PROJECT_ID}

#TODO terraform to re-deploy cloud-run instead
#bash "$DIR"/cloudrun/startpipeline/deploy.sh
#bash "$DIR"/cloudrun/queue/deploy.sh

#PYTHONPATH=$BASE_DIR/common/src python microservices//extraction_service/src/main.py