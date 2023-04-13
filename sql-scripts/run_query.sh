#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/../SET"

SCRIPT=$1

echo "Running $SCRIPT"

BIGQUERY_DATASET=validation
bq query --project_id="$PROJECT_ID" --dataset_id=$BIGQUERY_DATASET --nouse_legacy_sql  --flagfile="${DIR}/${SCRIPT}"

#bq query --project_id="$PROJECT_ID" --dataset_id=$BIGQUERY_DATASET --nouse_legacy_sql  --flagfile="${DIR}"/query_extraction_confidence.sql

