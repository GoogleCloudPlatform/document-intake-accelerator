DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$#" -lt 1 ]; then
    echo "Usage: "
    echo "  start_pipeline.sh <dir> [<gs_dir>]"
    echo "Copies files from <dir> to gs://${PROJECT_ID}/pa-forms/<gs_dir> and triggers START_PIPELINE"
    echo "  dir       - directory name with pdf files inside  or a path to a single form"
    echo "  gs_dir    - name of the directory inside  gs://${PROJECT_ID}/pa-forms/<gs_dir> (By default is copied as <dir>) "
    exit
fi
dir=$1
gs_dir=$dir

if [ "$#" -gt 1 ]; then
  gs_dir=$2
fi
GS_URL="gs://$PROJECT_ID-pa-forms/$gs_dir/"
INPUT=${DIR}/$dir
i=0
echo "------ $dir"
if [ -d "$dir"/ ]; then
  cd $dir
  echo "Using all PDF files inside directory $dir"
  for FILE in *.pdf; do
    i=$((i+1))
    URL="gs://$PROJECT_ID-pa-forms/${i}_$gs_dir/"
    echo " $i --- Copying data from ${INPUT}/${FILE} to ${URL}"
    gsutil cp "${INPUT}/${FILE}" "${URL}"
    # application form
#    gsutil cp "${DIR}/sample_data/bsc_demo/Package.pdf" "${URL}"
    echo "Triggering pipeline for ${URL}"
    gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${URL}"
#    echo "Sleeping to avoid exceeding the limit of concurrent requests to processor (Limit = 5)"
#    sleep 5
  done

  cd ..
#  gsutil -m cp "${INPUT}/*.pdf" "$GS_URL"
elif [ -f "$dir" ]; then
  # create a new case for each file for the demo purposes
  echo "Using single file $dir"
  echo "Copying data from ${INPUT} to ${GS_URL}"
  gsutil cp "${INPUT}" "$GS_URL"
  echo "Triggering pipeline for ${GS_URL}"
  gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${GS_URL}"
fi

#echo "Triggering pipeline for ${GS_URL}"
#gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${GS_URL}"


#./start_pipeline.sh sample_data/bsc_demo/ bsc

# DEMO
# ./start_pipeline.sh sample_data/pa-forms-10 pa001
# ./start_pipeline.sh sample_data/bsc_forms-10  bsc001