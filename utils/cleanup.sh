#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
"$DIR"/bq_cleanup.sh
"$DIR"/database_cleanup.sh

"$DIR"/gcs_cleanup.sh "gs://${PROJECT_ID}-pa-forms"
"$DIR"/gcs_cleanup.sh "gs://${PROJECT_ID}-document-upload"
"$DIR"/gcs_cleanup.sh "gs://${PROJECT_ID}-docai-output"


