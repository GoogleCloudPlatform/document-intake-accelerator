#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/../SET"

BIGQUERY_DATASET=validation
BIGQUERY_TABLE=validation_table

REGION=$(gcloud config get-value compute/region 2> /dev/null);
PROJECT_ID=$(gcloud config get-value core/project 2> /dev/null);
DELETE='DELETE FROM `'"${PROJECT_ID}"'`.'"${BIGQUERY_DATASET}."''"${BIGQUERY_TABLE}"' WHERE true; '

do_query()
{
  bq query --location=$REGION --nouse_legacy_sql \
  $DELETE
}

read -p "Are you sure you want to delete all BigQuery entries inside $PROJECT_ID.$BIGQUERY_DATASET.$BIGQUERY_TABLE? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
  echo "Cleaning Up then..."
  do_query
fi


