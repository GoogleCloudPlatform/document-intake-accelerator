#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR"/../../SET
export DEBUG=true
BUCKET=${PROJECT_ID}-pa-forms
FILE_PATH=${1:-"${DIR}/../../sample_data/splitter-test/Package-combined.pdf"}
echo "Using $FILE_PATH to ingest into the Pipeline.... "

FILE_PATH="${DIR}/../../sample_data/splitter-test/Package-combined.pdf"

# set GOOGLE_APPLICATION_CREDENTIALS
# set SPLITTER_ID
# set DOCAI_PROJECT_ID

DIR_OUT="${DIR}/../../sample_data/splitter-test/out"

if [ -z "$SPLITTER_ID" ]; then
  echo "SPLITTER_ID env variable must be set, exiting."
  exit
fi

if [ -z "$DOCAI_PROJECT_ID" ]; then
  echo "DOCAI_PROJECT_ID env variable must be set, exiting."
  exit
fi

if [ ! -d "$DIR_OUT" ] ; then
  mkdir "$DIR_OUT"
fi

# Do splitting into the pa-forms bucket
pip install -r "${DIR}"/../pdf-splitter/requirements.txt
python "${DIR}"/../pdf-splitter/main.py -f "${FILE_PATH}" --project-id "${DOCAI_PROJECT_ID}"  --processor-id $SPLITTER_ID -o "${DIR_OUT}"

"${DIR}"/../../start_pipeline.sh -d "${DIR_OUT}" -l split_extract -p

