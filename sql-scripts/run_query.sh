#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/../SET"

BIGQUERY_DATASET=validation
bq query --project_id="$PROJECT_ID" --dataset_id=$BIGQUERY_DATASET --nouse_legacy_sql  --flagfile="${DIR}"/query_extracted_entities.sql

#bq query --project_id="$PROJECT_ID" --dataset_id=$BIGQUERY_DATASET --nouse_legacy_sql  --flagfile="${DIR}"/query_extraction_confidence.sql

