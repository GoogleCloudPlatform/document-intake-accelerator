#!/usr/bin/env bash
set -e # Exit if error is detected during pipeline execution
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/SET

skaffold run  -p dev --default-repo=gcr.io/${PROJECT_ID}

#PYTHONPATH=$BASE_DIR/common/src python microservices//extraction_service/src/main.py