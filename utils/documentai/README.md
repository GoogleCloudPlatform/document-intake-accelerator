# Table of contents

- [Document AI Utilities](#document-ai-utilities)
  - [Prerequisites](#prerequisites)
    - [Install required libraries](#install-required-libraries)
    - [Set env variables](#set-env-variables)
    - [Create Service Account Key](#create-service-account-key)
    - [Assign required roles](#assign-required-roles)
    - [Verify assigned roles/permissions](#verify-assigned-rolespermissions)
    - [Setup application default authentication](#setup-application-default-authentication)
  - [Utilities and tools for CDA](#utilities-and-tools-for-cda)
    - [DocAI Utilities for CDA Debugging/Troubleshooting](#docai-utilities-for-cda-debuggingtroubleshooting)
      - [Prerequisites](#prerequisites)
      - [Classifier/Splitter Test](#classifiersplitter-test)
      - [Extraction Test](#extraction-test)
      - [Sort and Copy PDF files](#sort-and-copy-pdf-files)
      - [Get raw JSON output](#get-raw-json-output)
      - [Delete specific Firestore documents](#delete-specific-firestore-documents)

# Document AI Utilities

Below utility scripts help you debug DocumentAI for CDA Engine.

## Prerequisites

 ### Install required libraries 
```shell
  cd utils/documentai
  pip install -r requirements.txt
```

### Set env variables
Project you will be running experiments in:
```shell
  export PROJECT_ID=
  gcloud config set project $PROJECT_ID    
 ```

For each utility you might need an additional environment variables, they will be listed then.

### Create Service Account Key
You will need service account and service account key to execute utility scripts (via `GOOGLE_APPLICATION_CREDENTIALS` environment variable pointing to the service account key).

* Make sure to disable Organization Policy  preventing Service Account Key Creation
```shell
  gcloud services enable orgpolicy.googleapis.com
  gcloud org-policies reset constraints/iam.disableServiceAccountKeyCreation --project=$PROJECT_ID
```

* Create Service Account 

```shell
  export SA_NAME=docai-utility-sa
  export SA_EMAIL=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
  gcloud iam service-accounts create $SA_NAME \
          --description="Service Account for calling DocAI API and Document Warehouse API" \
          --display-name="docai-utility-sa"  

```

* Generate and Download Service Account key
```shell
    export KEY=${PROJECT_ID}_${SA_NAME}.json                     
    gcloud iam service-accounts keys create ${KEY}  --iam-account=${SA_EMAIL}
    export GOOGLE_APPLICATION_CREDENTIALS=${KEY}
```

### Assign required roles

```shell
  gcloud projects add-iam-policy-binding $PROJECT_ID \
          --member="serviceAccount:${SA_EMAIL}" \
          --role="roles/logging.logWriter"
                  
  gcloud projects add-iam-policy-binding $PROJECT_ID \
          --member="serviceAccount:${SA_EMAIL}" \
          --role="roles/storage.objectViewer"        
```

For each utility additional dedicated roles will be listed when required. 


### Verify assigned roles/permissions

* Verify assigned roles/permissions (you will need to have `getIamPolicy` role for both projects to see a list of assigned permissions):
```shell
  gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --format='table(bindings.role)' --filter="bindings.members:${SA_EMAIL}"
  gcloud projects get-iam-policy $DOCAI_PROJECT_ID --flatten="bindings[].members" --format='table(bindings.role)' --filter="bindings.members:${SA_EMAIL}"
```

### Setup application default authentication
```shell
gcloud auth application-default login
```

## Utilities and tools for CDA


### DocAI Utilities for CDA Debugging/Troubleshooting 

#### Prerequisites 
1. Make sure to follow ALL steps as described in the [prerequisites](#prerequisites) and export all variables as listed in there.
- `GOOGLE_APPLICATION_CREDENTIALS`
- `SA_NAME`
- `SA_EMAIL`
- `PROJECT_ID`

2. Set additional env variables:
```shell
  cd utils/documentai
  export DOCAI_PROJECT_ID=
  export API_DOMAIN=
  source ../../SET
```

3. Add required roles/permissions for the service account created in [prerequisites](#prerequisites) steps:

* For The DOCAI_PROJECT_ID:
  * `roles/documentai.apiUser`
  * `roles/documentai.editor`
  * `roles/logging.viewer`
  * `roles/storage.objectViewer`
  ~~~~
```shell
gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/documentai.apiUser"
gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/documentai.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/logging.viewer"
        
gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/storage.objectViewer"

```

#### Classifier/Splitter Test

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

#### Extraction Test
Make sure to do pre-requisite steps and set variables:
```shell
EXTERNAL=True;BASE_URL=https:/; python extract.py  -f gs://<path_to_form>.pdf -c form_class_name
```

**Sample output:**


#### Sort and Copy PDF files
TODO

#### Get raw JSON output
```shell
  export PROCESSOR_ID=
  export PROJECT_ID=<DOCAI_PROJECT_ID>
  python get_docai_json_response.py -f /local/path/to/file.pdf
```


#### Delete specific Firestore documents
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
