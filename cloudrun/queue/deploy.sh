DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PWD=$(pwd)
source "$DIR/../../SET"

gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID

if [ -z "$API_DOMAIN" ]; then
  echo API_DOMAIN is not set
  exit
fi

# get parameters
while getopts f: flag
do
  case "${flag}" in
    f) skip_common='true';;
  esac
done

echo "Running deployment for queue CloudRun with skip_common=[$skip_common]"
echo "Using IP address = $API_DOMAIN"

NAME="queue"
IMAGE="$NAME"
CLOUD_RUN="${NAME}-cloudrun"
SERVICE_ACCOUNT="cloudrun-${NAME}-sa@$PROJECT_ID.iam.gserviceaccount.com"

gcloud config set run/region $REGION
if [ -z "$skip_common" ]; then
  # Build common
  cd "${DIR}/../../common" || exit
  gcloud builds submit --region=$REGION  --substitutions=_IMAGE=common,_PROJECT_ID=${PROJECT_ID}
fi


# Build
cd "${DIR}" || exit
gcloud builds submit --region=$REGION  --substitutions=_IMAGE=${IMAGE},_PROJECT_ID=${PROJECT_ID}
gcloud run deploy ${CLOUD_RUN} --image="gcr.io/${PROJECT_ID}/${IMAGE}" \
 --allow-unauthenticated   --service-account=${SERVICE_ACCOUNT}   --set-env-vars=API_DOMAIN=${API_DOMAIN}   --set-env-vars=PROJECT_ID=${PROJECT_ID} --set-env-vars=BATCH_PROCESS_QUOTA=5 --set-env-vars=PROTOCOL=https --set-env-vars=IAP_SECRET_NAME=cda-iap-secret


cd "${PWD}" || exit