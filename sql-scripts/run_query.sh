#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#source "$DIR/../SET"

SCRIPT=$1
if [ -z "$SCRIPT" ]; then
  echo " Usage: ./run_query.sh QUERY_NAME"
  echo " Options:"
  echo "     - diagnose"
  echo "     - patient_names"
  echo "     - corrected_values"
  echo "     - entities"
  echo "     - confidence"

  exit
fi

#echo "Running $SCRIPT"
bq query --project_id="$PROJECT_ID" --dataset_id=$BIGQUERY_DATASET --nouse_legacy_sql  --flagfile="${DIR}/${SCRIPT}.sql"

#./run_query.sh query_extraction_confidence.sql
#./run_query.sh diagnose.sql

