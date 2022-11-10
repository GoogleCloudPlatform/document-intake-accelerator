#DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#source "${DIR}/SET"
INPUT_BUCKET="gs://${PROJECT_ID}-pa-forms"
gsutil cp START_PIPELINE "${INPUT_BUCKET}/test"