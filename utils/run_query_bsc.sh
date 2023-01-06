#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/../SET"

BATCH=$1
BIGQUERY_DATASET=validation
BIGQUERY_TABLE=validation_table

REGION=$(gcloud config get-value compute/region 2> /dev/null);
PROJECT_ID=$(gcloud config get-value core/project 2> /dev/null);
FROM_CL=' FROM `'"${PROJECT_ID}"'`.'"${BIGQUERY_DATASET}."''"${BIGQUERY_TABLE}"''


do_query()
{
  bq query --location=$REGION --nouse_legacy_sql \
   'SELECT case_id, uid, document_class, timestamp, '\
   ' JSON_EXTRACT(entities, '"'"'$.beneficiaryPhone'"'"') AS BeneficiaryPhone,'\
   ' JSON_EXTRACT(entities, '"'"'$.beneficiaryName'"'"') AS beneficiaryName,'\
   ' JSON_EXTRACT(entities, '"'"'$.beneficiaryDoB'"'"') AS beneficiaryDoB,'\
   ' JSON_EXTRACT(entities, '"'"'$.beneficiaryAddress'"'"') AS beneficiaryAddress,'\
   ' JSON_EXTRACT(entities, '"'"'$.beneficiaryZip'"'"') AS beneficiaryZip,'\
   ' JSON_EXTRACT(entities, '"'"'$.beneficiaryState'"'"') AS beneficiaryState,'\
   ' JSON_EXTRACT(entities, '"'"'$.diagCode'"'"') AS diagCode,'\
   ' JSON_EXTRACT(entities, '"'"'$.diagDescription'"'"') AS DiagDescription,'\
   ' JSON_EXTRACT(entities, '"'"'$.rpName'"'"') AS rpName,'\
   ' JSON_EXTRACT(entities, '"'"'$.spFacilityName'"'"') AS spFacilityName,'\
    $FROM_CL \
    ' WHERE STARTS_WITH(case_id, "'"$BATCH"'")'\
    ' ORDER BY timestamp'
}

title="Waiting for first data to be ingested into the BigQuery (this might take up to three minutes)... "
while true; do
  str=$(do_query)
  if [ -z "$str" ]; then
    if [ -z "$showed_title" ]; then
      echo $title
      showed_title=true
    fi
    echo "."
    sleep 5
  else
    echo "$str"
    break
  fi
done

#while grep do_query; do sleep 6; echo "test"; done

