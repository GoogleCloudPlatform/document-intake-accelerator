#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/../SET"
#query=`cat $DIR/corrected_values.sql`
#bq mk --use_legacy_sql=false --view "$query" \
#--project_id $PROJECT_ID --dataset_id $BIGQUERY_DATASET $BIGQUERY_DATASET.corrected_values
#
#
#query=`cat $DIR/entities.sql`
#bq mk --use_legacy_sql=false --view "$query" \
#--project_id $PROJECT_ID --dataset_id $BIGQUERY_DATASET $BIGQUERY_DATASET.entities
#
#query=`cat $DIR/confidence.sql`
#bq mk --use_legacy_sql=false --view "$query" \
#--project_id $PROJECT_ID --dataset_id $BIGQUERY_DATASET $BIGQUERY_DATASET.confidence


query=`cat $DIR/query_pa_forms_texas_flat.sql`
bq mk --use_legacy_sql=false --view "$query" \
--project_id $PROJECT_ID --dataset_id $BIGQUERY_DATASET $BIGQUERY_DATASET.pa_forms_texas_flat

query=`cat $DIR/query_pa_forms_bsc_flat.sql`
bq mk --use_legacy_sql=false --view "$query" \
--project_id $PROJECT_ID --dataset_id $BIGQUERY_DATASET $BIGQUERY_DATASET.pa_forms_bsc_flat