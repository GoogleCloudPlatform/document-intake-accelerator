DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$#" -lt 1 ]; then
    echo "Usage: "
    echo "  start_pipeline.sh <dir> [<gs_dir>]"
    echo "Copies files from sample_data/<dir> to gs://${PROJECT_ID}/pa-forms/<gs_dir> and triggers START_PIPELINE"
    echo "  dir       - directory name with pdf files inside sample_data directory"
    echo "  gs_dir    - name of the directory inside  gs://${PROJECT_ID}/pa-forms/<gs_dir> (By default is copied as <dir>) "
    exit
fi
dir=$1
gs_dir=$dir

if [ "$#" -gt 1 ]; then
  gs_dir=$2
fi
GS_URL="gs://$PROJECT_ID-pa-forms/$gs_dir/"
INPUT=${DIR}/sample_data/$dir
echo "Copying data from ${INPUT} to ${GS_URL}"
gsutil -m cp "${INPUT}/*" "$GS_URL"

echo "Triggering pipeline for ${GS_URL}"
gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${GS_URL}"
