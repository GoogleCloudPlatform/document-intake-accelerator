DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#source "${DIR}/SET"
FOLDER=$1

if [ -z "$FOLDER" ]; then
  FOLDER='test'
fi
INPUT_BUCKET="gs://${PROJECT_ID}-pa-forms"
gsutil cp "${DIR}"/START_PIPELINE "${INPUT_BUCKET}/${FOLDER}"