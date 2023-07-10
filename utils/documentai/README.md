# Document AI Test Utilities

Below utility scripts help you debug DocumentAI for CDA Engine.

## Prerequisites

You will need to have service account key with access to the GCS and DocumentAI

 ### 1. Install required libraries: 
```shell
    cd utils/documentai
    pip install -r requirements.txt
```

### 2. Set env variables:
```shell
    export DOCAI_PROJECT_ID=
    export PROJECT_ID=    
 ```

### 3. Set Service Account Key for executing scripts
You will need service account and service account key to execute utility scripts (via `GOOGLE_APPLICATION_CREDENTIALS` environment variable pointing to the service account key).

Following Roles need to be granted:
* For The DOCAI_PROJECT_ID:
  * `roles/documentai.apiUser`
  * `roles/documentai.editor`
  * `roles/logging.viewer`
* For the PROJECT_ID Project:
  * `roles/storage.objectViewer`

Fastest (and best for testing to verify that all required permissions are in place) is to use existing service account under PROJECT_ID (on which behalf all microservices for DOCAI processing are run under GKE ): `gke-sa@${PROJECT_ID}.iam.gserviceaccount.com` 


* Make sure to disable Organization Policy  preventing Service Account Key Creation
```shell
gcloud services enable orgpolicy.googleapis.com
gcloud org-policies reset constraints/iam.disableServiceAccountKeyCreation --project=$PROJECT_ID
```
* Generate and assign the Key
```shell
export SA_NAME=gke-sa
export SA_EMAIL=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
export KEY=${PROJECT_ID}_${SA_NAME}.json                     
gcloud iam service-accounts keys create ${KEY}  --iam-account=${SA_EMAIL}
export GOOGLE_APPLICATION_CREDENTIALS=${KEY}
```

* Verify assigned roles/permissions (you will need to have `getIamPolicy` role for both projects to see a list of assigned permissions):
```shell
gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --format='table(bindings.role)' --filter="bindings.members:${SA_EMAIL}"
gcloud projects get-iam-policy $DOCAI_PROJECT_ID --flatten="bindings[].members" --format='table(bindings.role)' --filter="bindings.members:${SA_EMAIL}"
```

As an alternative, following commands below will create Service Account with required permissions (though account executing commands must have permissions to vreate the role bindings, which might not always be a case):
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
        
gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/storage.objectViewer"
        
     
export KEY=${PROJECT_ID}_${SA_NAME}.json                     
gcloud iam service-accounts keys create ${KEY} \
        --iam-account=${SA_EMAIL}
                
export GOOGLE_APPLICATION_CREDENTIALS=${KEY}

```


### 4. Setup application default authentication
```shell
gcloud auth application-default login
```

## Utilities and tools for Testing/Debugging of CDA

**Description**:
Will use PDF form on he GCS bucket as an input and provide classification/splitter output using `classifier` processor from the CDA config file.

Make sure to do pre-requisite steps and set variables:
```shell
cd utils/documentai
export PROJECT_ID=
export API_DPMAIN=
export GOOGLE_APPLICATION_CREDENTIALS=
source ../../SET
```

### Classifier/Splitter Test

**Description**: 
Will use PDF form on he GCS bucket as an input and provide classification/splitter output using `classifier` processor from the CDA config file.

```shell
EXTERNAL=True;BASE_URL=https:/; python classify.py -f gs://<path_to_form>.pdf 
```

**Sample output:**

```shell
--(output omitted)--
Classification output (sub-documents split per pages):
gs://docs_for_testing/Package-combined.pdf
  {'predicted_class': 'fax_cover_page', 'predicted_score': 0.91, 'pages': (0, 0)}
  {'predicted_class': 'health_intake_form', 'predicted_score': 0.96, 'pages': (1, 1)}
  {'predicted_class': 'pa_form_texas', 'predicted_score': 0.92, 'pages': (2, 2)}
  {'predicted_class': 'pa_form_cda', 'predicted_score': 0.99, 'pages': (3, 3)}

```

### Extraction Test
Make sure to do pre-requisite steps and set variables:
```shell
EXTERNAL=True;BASE_URL=https:/; python extract.py  -f gs://<path_to_form>.pdf -c form_class_name
```

**Sample output:**


### Sort and Copy PDF files
TODO

### Get raw JSON output
```shell
  export PROCESSOR_ID=
  export PROJECT_ID=<DOCAI_PROJECT_ID>>
  python get_docai_json_response.py -f /local/path/to/file.pdf
```


### Delete specific Firestore documents
utils/database_cleanup_case_id_prefix.py - to delete specific records from the database using case_id prefix 


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
