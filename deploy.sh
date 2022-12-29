#!/usr/bin/env bash
set -e # Exit if error is detected during pipeline execution
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/SET
gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID
skaffold run  -p dev --default-repo=gcr.io/${PROJECT_ID}
bash "$DIR"/cloudrun/startpipeline/deploy.sh
bash "$DIR"/cloudrun/queue/deploy.sh

#PYTHONPATH=$BASE_DIR/common/src python microservices//extraction_service/src/main.py