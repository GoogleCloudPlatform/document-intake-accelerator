DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PWD=$(pwd)
source "$DIR/../../SET"
REGION=us-central1
NAME="queue"
IMAGE="$NAME"
CLOUD_RUN="${NAME}-cloudrun"
SERVICE_ACCOUNT="cloudrun-${NAME}-sa@$PROJECT_ID.iam.gserviceaccount.com"

gcloud config set run/region $REGION
# Build common
cd "${DIR}/../../common" || exit
gcloud builds submit --region=$REGION  --substitutions=_IMAGE=common,_PROJECT_ID=${PROJECT_ID}
cd "${DIR}" || exit

# Build
gcloud builds submit --region=$REGION  --substitutions=_IMAGE=${IMAGE},_PROJECT_ID=${PROJECT_ID}
gcloud run deploy ${CLOUD_RUN} --image="gcr.io/${PROJECT_ID}/${IMAGE}" \
 --allow-unauthenticated   --service-account=${SERVICE_ACCOUNT}   --set-env-vars=API_DOMAIN=${API_DOMAIN}   --set-env-vars=PROJECT_ID=${PROJECT_ID} --set-env-vars=MAX_UPLOADED_DOCS=1000

cd "${PWD}" || exit