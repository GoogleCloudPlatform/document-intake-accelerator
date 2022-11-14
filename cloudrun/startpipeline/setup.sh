# Create a trigger to filter events published to the Pub/Sub topic to our deployed Cloud Run service:
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PWD=$(pwd)
source "$DIR/../../SET"

START_PIPELINE_EVENTARC="start-pipeline-trigger"
START_PIPELINE_IMAGE="start-pipeline"
START_PIPELINE_RUN="startpipeline-cloudrun"
BUCKET_NAME="${PROJECT_ID}-pa-forms"
INPUT_BUCKET="gs://${BUCKET_NAME}"
SERVICE_ACCOUNT="cloudrun-sa@pa-document-ai.iam.gserviceaccount.com"

if gsutil ls | grep "${INPUT_BUCKET}"; then
    echo "Bucket [$INPUT_BUCKET] already exists - skipping step" INFO
else
    echo "Creating GCS bucket for pipeline: [INPUT_BUCKET]..."
    gsutil mb -p "$PROJECT_ID" "${INPUT_BUCKET}"/
    gsutil cp -r "${DIR}/../../data/forms/pa-forms" "${INPUT_BUCKET}/test"
    gsutil iam ch serviceAccount:"${SERVICE_ACCOUNT}":objectViewer "${INPUT_BUCKET}"
fi

gsutil iam ch serviceAccount:"${SERVICE_ACCOUNT}":objectViewer "${INPUT_BUCKET}"

gcloud builds submit --region=$REGION \
  --substitutions=_IMAGE=${START_PIPELINE_IMAGE},_PROJECT_ID=${PROJECT_ID}
  #,_SERVICE_NAME=${START_PIPELINE_RUN},_API_DOMAIN=${API_DOMAIN},_SERVICE_ACCOUNT=${SERVICE_ACCOUNT}

gcloud run deploy ${START_PIPELINE_RUN} --image="gcr.io/${PROJECT_ID}/${START_PIPELINE_IMAGE}" --allow-unauthenticated \
  --service-account=${SERVICE_ACCOUNT} \
  --set-env-vars=API_DOMAIN=${API_DOMAIN} \
  --set-env-vars=PROJECT_ID=${PROJECT_ID}

# In order to use Cloud Storage triggers, the Cloud Storage service agent
# must have the Pub/Sub Publisher (roles/pubsub.publisher) IAM role on your project.
# Grant the pubsub.publisher role to the Cloud Storage service account.
# This will allow the service account to publish events when START_PIPELINE file is
# uploaded into the bucket.
GCS_SERVICE_ACCOUNT=$(gsutil kms serviceaccount -p $PROJECT_NUMBER)
gcloud projects add-iam-policy-binding $PROJECT_NUMBER \
    --member "serviceAccount:$GCS_SERVICE_ACCOUNT" \
    --role "roles/pubsub.publisher"
#
#gcloud projects add-iam-policy-binding "$PROJECT_ID" \
#  --member="serviceAccount:$SERVICE_ACCOUNT" \
#  --role="roles/storage.admin"

#Grant the eventarc.eventReceiver role, so the service account can be used in a Cloud Storage trigger:
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --role "roles/eventarc.eventReceiver" \
  --member serviceAccount:${SERVICE_ACCOUNT}

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role='roles/pubsub.publisher'

if gcloud eventarc triggers list 2>/dev/null | grep "$START_PIPELINE_EVENTARC"; then
  :
else
  gcloud eventarc triggers create $START_PIPELINE_EVENTARC \
    --destination-run-service=$START_PIPELINE_RUN \
    --destination-run-path="/start-pipeline/run" \
    --destination-run-region=$REGION \
    --location="us" \
    --event-filters="type=google.cloud.storage.object.v1.finalized" \
    --event-filters="bucket=${BUCKET_NAME}" \
    --service-account=$SERVICE_ACCOUNT
fi



# update ackDeadline from the default 10 seconds
#TRIGGER_SUB=$(gcloud eventarc triggers describe $START_PIPELINE_TRIGGER --location=$REGION --format="value(transport.pubsub.subscription)")