DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PWD=$(pwd)
is_package='false'


# get parameters
while getopts d:l:p flag
do
  case "${flag}" in
    p) is_package='true';;
    d) FROM_DIR=${OPTARG};;
    l) gs_dir=${OPTARG};;
  esac
done

usage(){
    echo "Usage: "
    echo "  start_pipeline.sh -d <source_dir_or_file> [-l label_name] [-p]"
    echo "Copies files from <source_dir_or_file> to gs://${PROJECT_ID}/pa-forms/<gs_uri_dir> and triggers START_PIPELINE"
    echo "  -p       - All files inside same directory go as single CaseId (will not work when multiple files of same type)"
    exit
}


send_gcs_batch_processing(){
    FROM_URI=$1
    TO_URI=$2
    echo "Copying data from ${FROM_URI} to ${TO_URI}"
    gsutil cp "${FROM_URI}" "${TO_URI}"

}

if [ -z "$gs_dir" ]; then
  gs_dir="$(basename "$FROM_DIR")"
fi
GS_URL="gs://$PROJECT_ID-pa-forms/$gs_dir"

if [[ "$DIR" = /* ]]; then
  INPUT="${FROM_DIR}"
else
  INPUT="${PWD}/${FROM_DIR}"
fi

i=0

echo ">>> Source=[$FROM_DIR], Destination=[$GS_URL], packaged=$is_package"

if [ -d "$FROM_DIR"/ ]; then
  echo "Using all PDF files inside directory $FROM_DIR"

  if [ "$is_package" = "false" ]; then
    cd "$FROM_DIR" || exit;
    for FILE in *.pdf; do
      i=$((i+1))
      URL="gs://$PROJECT_ID-pa-forms/${gs_dir}_${i}/"
      echo " $i --- Copying data from ${INPUT}/${FILE} to ${URL}"
      gsutil cp "${INPUT}/${FILE}" "${URL}"
      echo "Triggering pipeline for ${URL}"
      gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${URL}"
    done
    cd ..
  else
    URL="gs://$PROJECT_ID-pa-forms/$gs_dir/"
    echo "Copying data from ${INPUT} to ${URL}"
    gsutil -m cp "${INPUT}/*.pdf" "${URL}/"
    echo "Triggering pipeline for ${URL}"
    gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${URL}"
  fi

#  gsutil -m cp "${INPUT}/*.pdf" "$GS_URL"
elif [ -f "$FROM_DIR" ]; then
  # create a new case for each file for the demo purposes
  echo "Using single file $FROM_DIR"
  echo "Copying data from ${INPUT} to ${GS_URL}"
  gsutil cp "${INPUT}" "$GS_URL"
  echo "Triggering pipeline for ${GS_URL}"
  gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${GS_URL}"

## Cloud Storage

elif [[ $FROM_DIR = gs://* ]]; then
  echo "Using Cloud Storage Location ${FROM_DIR}"
  if [ "$is_package" = "true" ]; then
    for SUB_DIR in $(gsutil list "${FROM_DIR}"); do
      echo $SUB_DIR
      if [[ "$SUB_DIR" == */ ]] && [[ "$SUB_DIR" !=  "$FROM_DIR/" ]] && [[ "$SUB_DIR" !=  "$FROM_DIR" ]]; then
        BASE_DIR="$(basename "$SUB_DIR")"
        URL="$GS_URL/$BASE_DIR/"
        for FILE in $(gsutil list "${SUB_DIR}"*.pdf 2>/dev/null); do
          send_gcs_batch_processing "$FILE" "$URL"
        done
        echo "Triggering pipeline for ${URL}"
        gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${URL}"
      elif [[ "$SUB_DIR" == *.pdf ]]; then
        FILE=$SUB_DIR
        send_gcs_batch_processing "$FILE" "$GS_URL/"
        TRIGGER_FILE_LINK="$GS_URL"

      fi
    done
    if [ -n "$TRIGGER_FILE_LINK" ]; then
        echo "Triggering pipeline for ${TRIGGER_FILE_LINK}"
        gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "$TRIGGER_FILE_LINK"
    fi

#    gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "$GS_URL"
  else
    for FILE in $(gsutil list "${FROM_DIR}"/*.pdf); do
      i=$((i+1))
      URL="${GS_URL}_${i}/"
      echo " $i --- Copying data from ${FILE} to ${URL}"
      gsutil cp "${FILE}" "${URL}"
      echo "Triggering pipeline for ${URL}"
      gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${URL}"
    done
  fi
fi


# DEMO Sample Commands:
# Will process all folders inside Batch1 as packaged cases
#./start_pipeline.sh -d gs://cda-001-engine-sample-forms/Batch1  -p

# What comes after -l - will also be used as a directory name inside pa-forms bucket
#./start_pipeline.sh -d gs://sample_data/bsc_demo -l demo-package
#./start_pipeline.sh -d sample_data/bsc_demo -l demo-package -p
# ./start_pipeline.sh -d sample_data/forms-10  -l demo-batch
# ./start_pipeline.sh -d sample_data/bsc_demo/bsc-dme-pa-form-1.pdf  -l demo-batch
# ./start_pipeline.sh -d sample_data/demo/form.pdf  -l test