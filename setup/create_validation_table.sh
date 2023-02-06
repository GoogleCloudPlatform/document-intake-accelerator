#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DATASET_ID="validation"

bq mk \
  --table \
  --project_id=$PROJECT_ID \
  --dataset_id=$DATASET_ID \
  --description="Used by CDA to keep track of documents processed" \
  --schema="$DIR/validation_table_schema.json" \
  "$DATASET_ID.validation_table"