# Quickstart Guide to Batch Upload Documents into the DocAi Warehouse

# Table of contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
    - [Provision DocAI Warehouse](#provision-docai-warehouse)
    - [Prepare GCS Bucket with Data](#prepare-gcs-bucket-with-data)
    - [Create OCR processor for extracting text data from the PDF forms](#create-ocr-processor-for-extracting-text-data-from-the-pdf-forms)
    - [Set Env Variables](#set-env-variables)
- [Setup](#setup)
- [Execution](#execution)
- [Troubleshooting](#troubleshooting)
    - [Error 403 IAM_PERMISSION_DENIED Permission Denied](#error-403-iam_permission_denied-permission-denied)
    - 
## Introduction
This is a utility that allows a batch upload of Folders/Files stored in GCS bucket into the Document WH using Processor to extract structured data.
- Right now default (with empty properties) schema will be created for the documents. In the future, automatic extraction of the schema based on the DocAI output will be added.
- There is no limit on 15 pages per document, since asynchronous bact processing is used by the DocAI parser.
- Processor could be in an external different project.
- GCS with data could be in the external project as well.
- Currently, only PDF files are handled.

This is a quick start guide with wrapper scripts, hiding all the magic.
If you want to follow the step-by-step guide yourself, refer to the following [steps](./STEP_BY_STEP_GUIDE.md).

## Prerequisites

### Provision DocAI Warehouse
- Create GCP Project wth a linked Billing Account
- Enable [Document AI Warehouse API](https://pantheon.corp.google.com/apis/library/contentwarehouse.googleapis.com) in your Google Cloud project and click Next.

- Provision the Instance:
    - For now, use `Universal Access: No document level access control` for the ACL modes in DocAI Warehouse and click Provision, then Next.
    - Provision DocAI warehouse Instance [Document AI Warehouse console](https://documentwarehouse.cloud.google.com) (which is external to the Google Cloud console).
    - You can skip Optional step for Service Account creation  and click Next
    - Click Done
- Follow link to Configure the Web Application:
    - Select Location (same as the location of the CDA and DocAI processors), Select Access Control (ACL) mode same as in the step before.
    - Click Create
    - Click "Search" in the top right corner -> This is where all documents will appear after the script execution is finished. 

### Prepare GCS Bucket with Data
- You can either use same project as created in previous step, or a different project under the same organization.
- Upload into GCS bucket files you want to load into the DocumentAI warehouse.
  - Currently, only PDF documents are supported.


- GCS bucket can have hierarchical structure, which will be reserved when loaded into the DocAI Warehouse.
- Docai WH Schema both for folders and documents will be the default one, without any properties. 


### Create OCR processor for extracting text data from the PDF forms
- You can either use same project as used for DocAI Warehouse, or use an existing Project with a processor. 
- Create a processor to parse the documents, such as OCR processor. 
- Note down Processor ID


### Set Env Variables
Following env variables need to be set for both setup and execution. 

```shell
export PROJECT_ID=  # This is the default ID for all Projects
export PROCESSOR_ID=

# Optional in case if different
export DOCAI_WH_PROJECT_ID=  # Project ID of the GCP Project in which DocAI WH has been provisioned
export DATA_PROJECT_ID=      # Project ID with GCS Data to be Loaded
export DOCAI_PROJECT_ID=     # Project ID of the GCP Project with DocAI Processor used for document parsing
```
## Setup 
Whenever setup is changed (env variables change as setup in the previous step), you will have to re-run setup script below.
```shell
cd utils/docai-wh
./setup_docai_wh.sh
```

## Execution
```shell
source SET
GOOGLE_APPLICATION_CREDENTIALS=${KEY_PATH}  python docai_wa_loaddocs.py -d gs://<PATH-TO-FOLDER> [-n <NAME-OF-THE-ROOT-FOLDER]
```
Parameters:
```shell
-d -  Path to the GCS storage folder, containing data with PDF documents to be loaded. All original structure of sub-folders will be preserved.
-n -  (optional) Name of the root folder inside DW where documents will be loaded. When skipped, will use the same name of the folder being loaded from.
```

Example:
```shell
GOOGLE_APPLICATION_CREDENTIALS=${KEY_PATH}  python docai_wa_loaddocs.py -d gs://ek-test-docwh-01 -n UM_Guidelines
```


## Troubleshooting 
### Error 403 IAM_PERMISSION_DENIED Permission Denied

  ```403 Permission 'contentwarehouse.documentSchemas.list' denied on resource '//contentwarehouse.googleapis.com/projects/35407211402/locations/us' (or it may not exist). [reason: "IAM_PERMISSION_DENIED"```
  
**Solution**: I have noticed it takes up to ten minutes for the roles to be properly propagated to the service account.
* Make sure all rights are properly assigned:
```shell
gcloud projects get-iam-policy $DOCAI_WH_PROJECT_ID --flatten="bindings[].members" --format='table(bindings.role)' --filter="bindings.members:${SA_EMAIL}"
```

Expected Output:
```shell
ROLE
ROLE: roles/contentwarehouse.admin
ROLE: roles/contentwarehouse.documentAdmin
ROLE: roles/documentai.apiUser
ROLE: roles/logging.logWriter
ROLE: roles/documentai.viewer
```

[//]: # (````shell)

[//]: # (gcloud projects get-iam-policy $DOCAI_PROJECT_ID --flatten="bindings[].members" --format='table&#40;bindings.role&#41;' --filter="bindings.members:${SA_EMAIL}")

[//]: # (````)
[//]: # (```shell)

[//]: # (  gcloud projects get-iam-policy $DATA_PROJECT_ID --flatten="bindings[].members" --format='table&#40;bindings.role&#41;' --filter="bindings.members:${SA_EMAIL}")

[//]: # (```)

[//]: # (Expected Output:)

[//]: # (```shell)

[//]: # (ROLE)

[//]: # (roles/storage.objectViewer)

[//]: # (```)