#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#source "$DIR/../SET"

SCRIPT=$1
LABEL=$2

if [ -z "$SCRIPT" ]; then
  echo " Usage: ./run_query.sh QUERY_NAME"
  echo " Options:"
  echo "     - diagnose"
  echo "     - patient_names"
  echo "     - corrected_values"
  echo "     - entities"
  echo "     - confidence"
  echo "     - count"
  exit
fi


FILTER="--parameter=LABEL:STRING:$LABEL"
#echo "Running $SCRIPT"
bq query --project_id="$PROJECT_ID" --dataset_id=$BIGQUERY_DATASET --nouse_legacy_sql "$FILTER" --flagfile="${DIR}/${SCRIPT}.sql" 2> /dev/null

#f=$( cat "${DIR}/${SCRIPT}.sql" )
#bq query --project_id="$PROJECT_ID" --dataset_id=$BIGQUERY_DATASET --nouse_legacy_sql "$FILTER" "$f"   2> /dev/null


#./run_query.sh query_extraction_confidence.sql
#./run_query.sh diagnose.sql

