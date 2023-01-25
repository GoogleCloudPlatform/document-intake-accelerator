DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
is_package='false'


# get parameters
while getopts d:l:p flag
do
  case "${flag}" in
    p) is_package='true';;
    d) dir=${OPTARG};;
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


if [ -z "$gs_dir" ]; then
  gs_dir=$dir
fi
GS_URL="gs://$PROJECT_ID-pa-forms/$gs_dir/"
INPUT=${DIR}/$dir
i=0

echo ">>> Source=[$dir], Destination=[$GS_URL], packaged=$is_package"

if [ -d "$dir"/ ]; then
  echo "Using all PDF files inside directory $dir"

  if [ "$is_package" = "false" ]; then
    cd "$dir" || exit;
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
    gsutil cp "${INPUT}/*" "${URL}/"
    echo "Triggering pipeline for ${URL}"
    gsutil cp "${DIR}"/cloudrun/startpipeline/START_PIPELINE "${URL}"
  fi

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
#./start_pipeline.sh -d sample_data/bsc_demo -l demo-package -p
# ./start_pipeline.sh -d sample_data/forms-10  -l demo-batch