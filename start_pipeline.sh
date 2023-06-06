DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PWD=$(pwd)
is_package='false'
date_str=$(date +%s )
set -e

# Setting Default BATCH_SIZE limit
BATCH_SIZE=50

# get parameters
while getopts d:l:p:b: flag
do
  case "${flag}" in
    p) is_package='true';;
    d) FROM_DIR=${OPTARG};;
    l) gs_dir=${OPTARG};;
    b) BATCH_SIZE=${OPTARG};;
  esac
done

usage(){
    echo "Copies files from <source_dir_or_file> to gs://${PROJECT_ID}/pa-forms/<label_name> and triggers START_PIPELINE"
    echo "Usage: "
    echo "  start_pipeline.sh -d <source_dir_or_file> [-l label_name] [-p]"
    echo "  -d       - Source directory or file, local or on GCS"
    echo "  -l       - Label name used for the case_id as prefix and as target folder  gs://${PROJECT_ID}/pa-forms/<label_name>"
    echo "  -p       - All files inside same directory go under same case_id (will not work when multiple files of same type)"
    echo "  -b       - Batch size to send to DocAI"

    echo
    echo "Sample Usage:"
    echo "./start_pipeline.sh -d gs://$PROJECT_ID-sample-forms/Batch1 -b 50"
    echo "./start_pipeline.sh -d gs://$PROJECT_ID-sample-forms/Batch1/form1.pdf"
    echo "./start_pipeline.sh -d sample_data/bsc_demo -l demo-batch"
    echo "./start_pipeline.sh -d sample_data/bsc_demo -l demo-batch -p"
    echo "./start_pipeline.sh -d sample_data/bsc_demo/form.pdf -l demo-batch"

# Will process all folders inside Batch1 as packaged cases
#./start_pipeline.sh -d gs://cda-001-engine-sample-forms/Batch1  -p

# What comes after -l - will also be used as a directory name inside pa-forms bucket
#./start_pipeline.sh -d gs://sample_data/bsc_demo -l demo-batch
#./start_pipeline.sh -d sample_data/bsc_demo -l demo-package -p
# ./start_pipeline.sh -d sample_data/forms-10  -l demo-batch
# ./start_pipeline.sh -d sample_data/bsc_demo/bsc-dme-pa-form-1.pdf  -l demo-batch
# ./start_pipeline.sh -d sample_data/demo/form.pdf  -l test
    exit
}

if [ -z "$FROM_DIR" ]; then
  usage
  exit
fi
send_gcs_batch_processing(){
    FROM_URI=$1
    TO_URI=$2
    echo "Copying data from ${FROM_URI} to ${TO_URI}"
    gsutil cp "${FROM_URI}" "${TO_URI}"

}

if [ -z "$gs_dir" ]; then
  gs_dir="$(basename "$FROM_DIR")"
fi
GS_URL_ROOT="gs://$PROJECT_ID-pa-forms/$date_str"
GS_URL="$GS_URL_ROOT/$gs_dir"


if [[ "$FROM_DIR" = /* ]]; then
  INPUT="${FROM_DIR}"
#  echo "absolute path"
else
  INPUT="${PWD}/${FROM_DIR}"
#  echo "relative path"
fi

i=1

echo ">>> Source=[$FROM_DIR], Destination=[$GS_URL_ROOT], packaged=[$is_package], batch_size=[$BATCH_SIZE]"

if [ -d "$INPUT"/ ]; then
  echo "Using all PDF files inside directory $INPUT"

  if [ "$is_package" = "false" ]; then
    cd "$INPUT" || exit;
    for FILE in *.pdf; do
      URL="${GS_URL}_${i}/"
#      if ! (($i % 5)); then
#          echo "Waiting for previous batch job to be done due to Quota Limits"
#          sleep 60
#      fi
      echo " $i --- Copying data from ${INPUT}/${FILE} to ${URL}"
      gsutil cp "${INPUT}/${FILE}" "${URL}"
      i=$((i+1))
    done
    echo ">> Triggering pipeline for ${GS_URL_ROOT}"
    gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${GS_URL_ROOT}/"
    cd ..
  else
    echo ">> Copying data from ${INPUT} to ${GS_URL}"
    gsutil -m cp "${INPUT}/*.pdf" "${GS_URL}/"
    echo ">> Triggering pipeline for ${GS_URL}"
    gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${GS_URL}"
  fi

#  gsutil -m cp "${INPUT}/*.pdf" "$GS_URL"
elif [ -f "$FROM_DIR" ]; then
  # create a new case for each file for the demo purposes
  echo ">> Using single file $FROM_DIR"
  echo ">> Copying data from ${INPUT} to ${GS_URL}/"
  gsutil cp "${INPUT}" "${GS_URL}/"
  echo ">> Triggering pipeline for ${GS_URL}"
  gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${GS_URL}/"

## Cloud Storage
elif [[ $FROM_DIR = gs://* ]]; then
  echo ">> Using Cloud Storage Location ${FROM_DIR}"
  if [ "$is_package" = "true" ]; then
    for SUB_DIR in $(gsutil list "${FROM_DIR}"); do
      #echo $SUB_DIR
      if [[ "$SUB_DIR" == */ ]] && [[ "$SUB_DIR" !=  "$FROM_DIR/" ]] && [[ "$SUB_DIR" !=  "$FROM_DIR" ]]; then
        BASE_DIR="$(basename "$SUB_DIR")"
        URL="$GS_URL/$BASE_DIR/"
        for FILE in $(gsutil list "${SUB_DIR}"*.pdf 2>/dev/null); do
          send_gcs_batch_processing "$FILE" "$URL"
        done
        echo ">> Triggering pipeline for ${URL}"
        gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${URL}"
      elif [[ "$SUB_DIR" == *.pdf ]]; then
        FILE=$SUB_DIR
        send_gcs_batch_processing "$FILE" "$GS_URL/"
        TRIGGER_FILE_LINK="$GS_URL"

      fi
    done
    if [ -n "$TRIGGER_FILE_LINK" ]; then
        echo ">> Triggering pipeline for ${TRIGGER_FILE_LINK}"
        gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "$TRIGGER_FILE_LINK"
    fi

#    gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "$GS_URL"
  else
    # It can be a stand-alone file or a directory
    #echo $FROM_DIR
    if [[ $FROM_DIR = *.pdf ]] || [[ $FROM_DIR = *.PDF ]]; then
        URL="${GS_URL}"
        echo ">> Copying data from ${FROM_DIR} to ${URL}"
        gsutil cp "${FROM_DIR}" "${URL}/"
        echo ">> Triggering pipeline for ${GS_URL_ROOT}"
        gsutil -m cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${GS_URL_ROOT}/"
    else
      if [ -z "$BATCH_SIZE" ]; then
        for FILE in $(gsutil list "${FROM_DIR}"/*.pdf); do
          URL="${GS_URL}_${i}/"
          echo " $i -- Copying data from ${FILE} to ${URL}"
          gsutil -m cp "${FILE}" "${URL}"
          i=$((i+1))
        done
        echo ">> Triggering pipeline for ${GS_URL_ROOT}"
        gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${GS_URL_ROOT}"
      else
        BATCH_NUM=1
        i=1
        echo "Starting $BATCH_NUM Batch"
        for FILE in $(gsutil list "${FROM_DIR}"/*.pdf); do
          BASE_DIR=${GS_URL}/batch_${BATCH_NUM}
          URL="${BASE_DIR}/${gs_dir}_${i}/"
          echo " $i -- Copying data from ${FILE} to ${URL}"
            gsutil cp "${FILE}" "${URL}"
#          echo $i, $(($i % $BATCH_SIZE))
          if ! (($i % $BATCH_SIZE)); then
            echo ">> Triggering pipeline for ${BASE_DIR}/"
            gsutil -m cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${BASE_DIR}/"
            BATCH_NUM=$((BATCH_NUM+1))
            echo "Starting $BATCH_NUM Batch"
            TRIGGERED='true'
          else
            TRIGGERED='false'
          fi
          i=$((i+1))
        done
        if [[ $TRIGGERED == "false" ]]; then
            echo ">> Triggering pipeline for ${BASE_DIR}/"
            gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${BASE_DIR}/"
        fi

      fi
    fi
  fi
else
    echo "Error: $INPUT is not a valid directory"
fi


# DEMO Sample Commands:
# Will process all folders inside Batch1 as packaged cases
#./start_pipeline.sh -d gs://cda-001-engine-sample-forms/Batch1  -p

# What comes after -l - will also be used as a directory name inside pa-forms bucket
#./start_pipeline.sh -d gs://sample_data/bsc_demo -l demo-batch
#./start_pipeline.sh -d sample_data/bsc_demo -l demo-package -p
# ./start_pipeline.sh -d sample_data/forms-10  -l demo-batch
# ./start_pipeline.sh -d sample_data/bsc_demo/bsc-dme-pa-form-1.pdf  -l demo-batch
# ./start_pipeline.sh -d sample_data/demo/form.pdf  -l test