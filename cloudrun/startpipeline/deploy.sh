DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PWD=$(pwd)
source "$DIR/../../SET"

NAME="startpipeline"

gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID

export TF_VAR_admin_email=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")

if [[ -z "${API_DOMAIN}" ]]; then
  echo API_DOMAIN env variable is not set. Using External Ingress IP address...
  export API_DOMAIN=$(kubectl describe ingress default-ingress | grep Address | awk '{print $2}')
  echo API_DOMAIN="$API_DOMAIN"
fi

export TF_VAR_api_domain=$API_DOMAIN
echo "Using IP address = $TF_VAR_api_domain"


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
 --allow-unauthenticated   --service-account=${SERVICE_ACCOUNT}   --set-env-vars=API_DOMAIN=${API_DOMAIN}   --set-env-vars=PROJECT_ID=${PROJECT_ID}

# trigger batch upload
#bash "$DIR/start_pipeline.sh" 'test'
#cd "${PWD}" || exit