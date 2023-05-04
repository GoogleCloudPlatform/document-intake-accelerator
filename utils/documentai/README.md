# Document AI Test Utilities

Below utility scripts help you debug DocumentAI for CDA Engine.

## Prerequisites

You will need to have service account key with access to the GCS and DocumentAI

1. Install the prerequisites: 
```shell
    cd utils/documentai
    pip install -r requirements.txt
    export GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_key_account>
```

2. Granting Access and Permissions
   1. When running from the development machine, setup application default authentication, run: `gcloud auth application-default login`
   2. When running from Cloud Shell, `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to the service account key with required storage (input/output gcs bucket) and [DOCAI permissions](https://cloud.google.com/document-ai/docs/access-control/iam-roles):

## Utilities

### Sort and Copy PDF files
TODO
### Get raw JSON output
```shell
  export PROCESSOR_ID=
  export PROJECT_ID=<DOCAI_PROJECT_ID>>
  python get_docai_json_response.py -f /local/path/to/file.pdf
```

`Pre-requisite`: Disable org policy preventing Service Account Key Creation

1. Create service account you will use to run debugging scripts
2. Grant following permissions:
   1. Access to docai projects as DocAI viewer, Logging Viewer, Storage Viewer, Doc AI API User
   2. Access as editor to CDA deployment project
3. Download service Account key

```shell
    export DOCAI_PROJECT_ID=
    export PROJECT_ID=
    
 ```

```shell
SA_NAME=cda-docai
SA_EMAIL=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

gcloud config set project $PROJECT_ID
gcloud iam service-accounts create $SA_NAME \
        --description="Doc AI invoker" \
        --display-name="cda docai invoker"
    
# DOCAI Access
gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/documentai.apiUser"
gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/documentai.editor"

gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/logging.viewer"
        
gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/storage.objectViewer"
        
     
export KEY=${PROJECT_ID}_${SA_NAME}.json                     
gcloud iam service-accounts keys create ${KEY} \
        --iam-account=${SA_EMAIL}
                
export GOOGLE_APPLICATION_CREDENTIALS=${KEY}

```

To list roles 
```shell
gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --format='table(bindings.role)' --filter="bindings.members:${SA_NAME}
```

Setup cross Project access if you have not done so:
```shell
./setup/setup_docai_access.sh
```

When using Cloud Storage to send documents for DocAI, make sure, `DocumentAI Core Service Agent` service account has access to the cloud storage bucket.

Easiest, is to assign Cloud Storage Viewer rights to the whole project:

```shell
PROJECT_DOCAI_NUMBER=$(gcloud projects describe "$DOCAI_PROJECT_ID" --format='get(projectNumber)')
SA_DOCAI="service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_DOCAI"  --role="roles/storage.objectViewer"  2>&1
gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --format='table(bindings.role)' --filter="bindings.members:${SA_DOCAI}"
```

Otherwise, assign Viewer Access per dedicated Bucket (replace `<YOUR_BUCKET_HERE>` accordingly):
```shell
  gcloud storage buckets add-iam-policy-binding  gs://<YOUR_BUCKET_HERE> --member="serviceAccount:$SA_DOCAI" --role="roles/storage.objectViewer"  2>&1

```
