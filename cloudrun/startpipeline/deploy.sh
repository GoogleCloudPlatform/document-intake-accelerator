DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PWD=$(pwd)
source "$DIR/../../SET"
REGION=us-central1
START_PIPELINE_IMAGE="start-pipeline"
START_PIPELINE_RUN="startpipeline-cloudrun"
SERVICE_ACCOUNT="cloudrun-sa@pa-document-ai.iam.gserviceaccount.com"

# Build common
cd "${DIR}/../../common" || exit
gcloud builds submit --region=$REGION  --substitutions=_IMAGE=common,_PROJECT_ID=${PROJECT_ID}
cd "${DIR}" || exit

# Build start-pipeline
gcloud builds submit --region=$REGION  --substitutions=_IMAGE=${START_PIPELINE_IMAGE},_PROJECT_ID=${PROJECT_ID}
gcloud run deploy ${START_PIPELINE_RUN} --image="gcr.io/${PROJECT_ID}/${START_PIPELINE_IMAGE}" \
 --allow-unauthenticated   --service-account=${SERVICE_ACCOUNT}   --set-env-vars=API_DOMAIN=${API_DOMAIN}   --set-env-vars=PROJECT_ID=${PROJECT_ID}

# trigger batch upload
bash "$DIR/start_pipeline.sh" 'test'
cd "${PWD}" || exit