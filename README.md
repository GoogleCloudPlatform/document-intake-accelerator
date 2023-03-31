# Claims Data Activator (CDA)

## Introduction
> A pre-packaged and customizable solution to accelerate the development of end-to-end document processing workflow incorporating Document AI parsers and other GCP products (Firestore, BigQuery, GKE, etc). The goal is to accelerate the development efforts in document workflow with many ready-to-use components.

## Key features
- End-to-end workflow management: document classification, extraction, validation, profile matching and Human-in-the-loop review.
- API endpoints for integration with other systems.
- Customizable components in microservice structure.
- Solution architecture with best practices on Google Cloud Platform.


## How To Use This Repo
This repo is intended to be used as a reference for your own implementation and
as such we designed many elements to be as generic as possible. 
You will almost certainly need to modify elements to fit your organization's specific requirements. 
We strongly recommend you fork this repo, so you can have full control over your unique setup.
While you will find end-to-end tools to help spin up a fully functional sandbox environment, most likely you will find yourself customizing solution further down the line.  

## Prerequisites

### Project(s) Creation
It is recommended to deploy into two projects: one for the CDA Pipeline Engine (`PROJECT_ID`), and another for the Document AI processors (`DOCAI_PROJECT_ID`). Both projects need to belong to the same Org.
When following this  practice, before deployment create two projects and note down.

### Classifier Access
Classifier is currently in Preview. Early access can be granted using this [form](https://docs.google.com/forms/d/e/1FAIpQLSfDuC9bGyEwnseEYIC3I2LvNjzz-XZ2n1RS4X5pnIk2eSbk3A/viewform), so that Project is whitelisted.

### Domain Name Registration
For this solution you need a valid domain name registered.


### Installation Using Cloud Shell

Following steps describe installation using Google Cloud Shell console.
Make sure to clone this repository before starting.

*Important*: User needs to have Project **owner** role in order to deploy  terraform setup.

## Preparations

### Reserving External IP
For this solution you need to reserve an external global IP in the CDA Engine Project, that will be used for the Ingress and bound to the Domain name (if used).
This could be done from the GCP console, or by running following Cloud Shell commands:

From the GCP Console:
- Go to VPC networks (you will have to enable Compute Engine API)
- Go to IP addresses and reserve External **global** Static IP address with a chosen ADDRESS_NAME (for example, `cda-ip`).
- Note down the name given.

From the Cloud Shell:
```shell
export PROJECT_ID=
gcloud config set project $PROJECT_ID
gcloud services enable compute.googleapis.com
gcloud compute addresses create cda-ip  --global
```

To see the reserved IP:
```shell
gcloud compute addresses describe cda-ip --global
```

Copy terraform sample variable file:
 ```shell
cp terraform/environments/dev/terraform.sample.tfvars terraform/environments/dev/terraform.tfvars
```

Verify `cda_external_ip` points to the reserved External IP name inside `terraform/environments/dev/terraform.tfvars`:
 ```
 cda_external_ip = "cda-ip"   #IP-ADDRESS-NAME-HERE
 ```

### When deploying using Shared VPC
As is often the case in real-world configurations, this blueprint accepts as input an existing [Shared-VPC](https://cloud.google.com/vpc/docs/shared-vpc) via the `network_config` variable inside [terraform.tfvars](terraform/environments/dev/terraform.tfvars).
For the preparation steps to set up VPC Host Project and Service project, refer to the steps described in [here](docs/SharedVPC_steps.md).

 - Edit `terraform/environments/dev/terraform.tfvars` in the editor,  uncomment `network_config` and fill in required parameters inside `network_config` (when using the [steps](docs/SharedVPC_steps.md), only need to set `HOST_PROJECT_ID`:
 ```
network_config = {
  host_project      = "HOST_PROJECT_ID"
  network = "cda-vpc"   #SHARED_VPC_NETWORK_NAME"
  subnet  = "tier-1"    #SUBNET_NAME
  gke_secondary_ranges = {
    pods     = "tier-1-pods"       #SECONDARY_SUBNET_PODS_RANGE_NAME
    services = "tier-1-services"   #SECONDARY_SUBNET_SERVICES_RANGE_NAME"
  }
  region = "us-central1"
}
```

When the **default GKE Control Plane CIDR Range (172.16.0.0/28) overlaps** with your network:
 - Edit `terraform.tfvars` in the editor, uncomment `master_ipv4_cidr_block` and fill in the value of the GKE Control Plane CIDR /28 range:
 ```shell
 master_ipv4_cidr_block = "MASTER.CIDR/28.HERE"
 ```


### Configure DNS `A` record for your domain with IP address reserved above

You can use gcloud command to get information about reserved address.
```shell
gcloud compute addresses describe cda-ip --global
```

- From Cloud DNS, click on CREATE ZONE.
- Create a DNS record set of type A and point to the reserved external IP:
  - On the Zone details page, click Add record set.
  - Select A from the Resource Record Type menu.
- For IPv4 Address, enter the external IP address that have been reserved.

Once configured, verify that your domain name resolves to the reserved IP address.

  ```bash
  $ nslookup -query=a mydomain.com
  ...(output omitted)..

  ```

### IAP setup

IAP setup can be done from [Google Cloud Console](https://console.cloud.google.com/).

1. Configure oAuth consent screen

  * Browse to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
  * Select desired usage type: *Internal* or *External* and click **Create** button
  * As a minimum, fill all required fields: **app name**, **user support email**,
    **developer contact email**
  * Click **Save and Continue** button

2. Configure oAuth credentials

  * Browse to [API & Services Credentials screen](https://console.cloud.google.com/apis/credentials/)
  * Click **Create Credentials** from bottom menu and select *OAuth Client ID* from drop-down list
  * Select *Web application* as application type
  * Fill name of your oAuth client
  * Click **Create** button
  * Once client is created, select it from the list to open details page
  * Notice **Client ID** and **Client Secret**  - you will use them in later configurations.
    They can be also downloaded in JSON format.
  * Add **Authorized redirect URI** in a format `https://iap.googleapis.com/v1/oauth/clientIds/CLIENT_ID:handleRedirect`
    *(replace CLIENT_ID with your valid one)*

### Configure GKE secret

Create kubernetes secret with oAuth client credentials from the previous step  [IAP setup prerequisite](#prerequisite-iap-setup)

```shell
export CLIENT_ID=
export CLIENT_SECRET=
```
   ```bash
   kubectl create secret generic cda-iap \
   --from-literal=client_id=$CLIENT_ID \
   --from-literal=client_secret=$CLIENT_SECRET
   ```

### Enable IAP on backend services

Once backend service is created, enable IAP protection on it and update IAM policies.
This can be done from [Google Cloud Console](https://console.cloud.google.com/).

* Browse to [Identity-Aware Proxy](https://console.cloud.google.com/security/iap) page
* Locate your backend service on a resources list under *HTTPS Resources* tab
* **Toggle IAP protection** for your backend service
* Select checkbox next to your service so that info panel appears on the right
* Click **Add Member** button on the right panel to add members
* Add *Google Account* or  *Service Account* with **IAP-secured Web App User** role


#### Environment Variables
```shell
export API_DOMAIN=<YOUR_DOMAIN>
export PROJECT_ID=<GCP Project ID to host CDA Pipeline Engine>
```

Optionally, when deploying processors to different Project:
```shell
export DOCAI_PROJECT_ID=<GCP Project ID to host Document AI processors> #
```

### Steps when **NOT** using a domain

#### Changes to Ingress
In the file `terraform/modules/ingress/main.tf` comment out Line 79: 
`// host = var.domain` 
> The host is needed for HTTPS connection to work, but require a valid DNS name and will not work with the IP address.

#### Environment Variables
```shell
export API_DOMAIN=<STATIC_IP_ADDRESS_RESERVED>
export PROJECT_ID=<GCP Project ID to host CDA Pipeline Engine>
```

Optionally, when deploying processors to different Project:
```shell
export DOCAI_PROJECT_ID=<GCP Project ID to host Document AI processors> #
```


## Installation
### Terraform 
Run init step (will prepare for terraform execution and do terraform apply with auto-approve):
```shell
./init.sh
```

> If Cloud shell times out during the operation, a workaround is to use `nohup` command to make sure a command does not exit when Cloud Shell times out.
>
>  ```shell
>  nohup bash -c "time ./init.sh" &
>  tail -f nohup.out
>  ```

  
### Enable Firebase Auth
- Before enabling firebase, make sure [Firebase Management API](https://console.cloud.google.com/apis/api/firebase.googleapis.com/metrics) should be disabled in GCP API & Services.
- Go to [Firebase Console UI](https://console.firebase.google.com/) to add your existing project. Select “Pay as you go” and Confirm plan.
- On the left panel of Firebase Console UI, go to Build > Authentication, and click Get Started.
- Select Email/Password as a Sign in method and click Enable.
- Go to users and add email/password for a valid Sign in method.
[//]: # (- Enable Google auth provider, and select Project support email to your admin’s email. Leave the Project public-facing name as-is. Then click Save.)
- Go to Settings > Authorized domain, add the following to the Authorized domains:
  - Web App Domain (e.g. adp-dev.cloudpssolutions.com) - or skip this step if you do not have a custom domain.
  - API endpoint IP address (Reserved External IP address)
- Go to Project Overview > Project settings, you will use this info in the next step.
- In the codebase, open up microservices/adp_ui/.env in an Editor (e.g. VSCode), and change the following values accordingly.
  - REACT_APP_BASE_URL
    - `https://<your_domain_name>` The custom Web App Domain that you added in the previous step. Make sure to use `https`
    - Alternatively, you can use the API Domain IP Address (Ingress), Reserved External IP address e.g. http://123.123.123.123 (not https)
  - REACT_APP_FIREBASE_API_KEY - Web API Key
  - REACT_APP_FIREBASE_AUTH_DOMAIN - $PROJECT_ID.firebaseapp.com
  - REACT_APP_STORAGE_BUCKET - $PROJECT_ID.appspot.com
  - REACT_APP_MESSAGING_SENDER_ID
    - You can find this ID in the Project settings > Cloud Messaging
  - (Optional) REACT_APP_MESSAGING_SENDER_ID - Google Analytics ID, only available when you enabled the GA with Firebase.

### Deploy microservices

With kustomize 5.0 there are breaking changes on passing the environment variables.
While we are making solution to account for those changes and work with kustomize 5.0, as a temporal workaround, please be sure to downgrade to 4.5.7 version when using Cloud Shell:
```shell
kustomize version
sudo rm /usr/local/bin/kustomize
curl -Lo install_kustomize "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" && chmod +x install_kustomize
sudo ./install_kustomize 4.5.7 /usr/local/bin
kustomize version
```

```shell
./deploy.sh
```

### Out of the box Demo Flow

Quick test to trigger pipeline to parse  the sample form:
```shell
./start_pipeline.sh -d sample_data/bsc_demo/bsc-dme-pa-form-1.pdf  -l demo-batch
```

#### Working from the UI
In order to access the Application UI, Navigate to the API Domain IP Address or Domain Name (depending on the setup) in the browser and login with your Google credentials.
Try Uploading the Document, using *Upload a Document* button.  From *Choose Program* drop-down, select a state ( pick any ).
Right now, the Form Processor is set up as a default processor (since no classifier is deployed or trained), so each document will be processed with the Form Parser and extracted data will be streamed to the BigQuery.

> The setting for the default processor is done through the following configuration setting  "settings_config" -> "classification_default_label".  Explained in details in the [Configuring the System](#system_config).

As you click Refresh Icon on the top right, you will see different Status the Pipeline goes through: *Classifying -> Extracting -> Approved* or *Needs Review*.

If you select *View* action, you will see the key/value pairs extracted from the Document.

Navigate to BigQuery and check for the extracted data inside `validation` dataset and `validation_table`.

You could also run sample query from the Cloud Shell:
```shell
./sql-scripts/run_query.sh
```

#### Triggering pipeline in a batch mode
*NB: Currently only pdf documents are supported, so if you have a jpg or png, please first convert it to pdf.*

For example, to trigger pipeline to parse  the sample form:
```shell
./start_pipeline.sh -d sample_data/bsc_demo/bsc-dme-pa-form-1.pdf  -l demo-batch
```

> The Pipeline is triggered when an empty file named START_PIPELINE is uploaded to the `${PROJECT_ID}-pa-forms` GCS bucket. When the START_PIPELINE document is uploaded, all `*.pdf` files containing in that folder are sent to the processing queue.  
> All documents within the same gsc folder are treated as related documents, that belong to the same application (patient).
> When processed, documents are copied to `gs://${PROJECT_ID}-document-upload` with unique identifiers.
>
> Wrapper script to upload each document as a standalone application inside `${PROJECT_ID}-pa-forms`:
> ```shell
> ./start_pipeline.sh -d <local-dir-with-forms>  -l <batch-name>
> ```
>
> Or send all documents within the directory as single Application with same Case ID:
> ```shell
> ./start_pipeline.sh -d <local-dir-with-forms> -l <batch-name> -p
> ```
>
> Or send a pdf document by name:
> ```shell
> ./start_pipeline.sh -d <local-dir-with-forms>/<my_doc>.pdf  -l <batch-name>
> ```
>
> Alternatively, send a single document to processing:
> - Upload *pdf* form to the gs://<PROJECT_ID>-pa-forms/my_dir and
> - Drop empty START_PIPELINE file to trigger the pipeline execution.
> After putting START_PIPELINE, the pipeline is automatically triggered  to process  all PDF documents inside the gs://${PROJECT_ID}-pa-forms/<mydir> folder.
>
> ```shell
> gsutil cp  <my-local-dir>/<my_document>.pdf
> gsutil cp START_PIPELINE gs://${PROJECT_ID}-pa-forms/<my-dir>/
> touch START_PIPELINE
> gsutil cp START_PIPELINE gs://${PROJECT_ID}-pa-forms/<my-dir>/
> ```


## <a name="https"></a>Adding HTTPS after deployment 
If you have deployed solution using IP address and now want to migrate to domain+https, there are few steps to be done for that. 

- From Cloud DNS, click on CREATE ZONE and create new zone.
- Create a DNS record set of type A and point to the IP address of the Ingress (Reserved External IP).
  - On the Zone details page, click Add record set.
  - Select A from the Resource Record Type menu.
  - For IPv4 Address, enter the external IP address that have been reserved.

Uncomment line 79 in `terraform/modules/ingress/main.tf`:
//      host = var.domain

**Re-apply terraform modules:**
```shell
export PROJECT_ID=<your CDA service project ID>
export API_DOMAIN=<your_domain_here>
./setup/init_domain.sh
```

**Update Firebase settings:**
- In the codebase, open up microservices/adp_ui/.env in an Editor (e.g. VSCode), and change the following value accordingly.
  - REACT_APP_BASE_URL
    - `https://<your_domain_name>` The custom Web App Domain that you added in the previous step. Make sure to use `https`

- Go to [Firebase Console UI](https://console.firebase.google.com/).
- On the left panel of Firebase Console UI, go to Build > Authentication -> Settings > Authorized domain. Add your domain to the list:
  - Web App Domain (e.g. adp-dev.cloudpssolutions.com).


**Re-Deploy microservices**
```shell
- ./deploy.sh
```

**Debugging**

- To validate if valid certificate was created:

```shell
kubectl get certificate
```

```shell
kubectl describe certificate
```

```shell
kubectl describe ing default-ingress
```

To force re-creation of the certificate, delete and create ingress manually:
```shell
kubectl get ing default-ingress -o yaml > ingress.yaml
cat ingress.yaml
```

```shell
kubectl delete  ing default-ingress
```

```shell
kubectl apply -f ingress.yaml
```



## Installation from the developer machine

For the in-depth instructions please refer to this [page](#steps_original.md).

[//]: # ()
[//]: # (In order to run the example and deploy on a shared VPC the identity running Terraform must have the following IAM role on the Shared VPC Host project.)

[//]: # (- Compute Network Admin &#40;roles/compute.networkAdmin&#41;)

[//]: # (- Compute Shared VPC Admin &#40;roles/compute.xpnAdmin&#41;)


## Setting up CDE and CDS 

**Pre-requisites** 
- There should be at least 20 (recommended 50) customer  forms with filled data (of the same type), which could be used for training the processor for extraction and classification.
- All forms need to be in pdf format


If you have png files, following script can convert them to pdf:
```shell
python3 -m pip install --upgrade Pillow
python utils/fake_data_generation/png2pdf.py -d sample_data/<input-dir> -o sample_data/<output_pdf_dir>
```

### Custom Document Extractor
The Custom Document Extractor has already been deployed, but not yet trained. The steps need to be done manual and via the UI.
- Manually Configure and [Train Custom Document Extractor](https://cloud.google.com/document-ai/docs/workbench/build-custom-processor) (currently it is deployed but not pre-trained)
  - Using UI Manually Label and Train Custom Document Extractor to recognize selected type of the PriorAuth forms.
  - Set a default revision for the processor.
  - Test extraction by manually uploading document via the UI and check how entities are being extracted and assigned labels.

You can deploy and train additional Custom Document Extractor if you navigate to **Document AI -> Workbench** and select **Custom Document Extractor** -> CREATE PROCESSOR

### Custom Document Classifier
Classifier allows mapping the document class to the processor required for data extraction. 

Configure Custom Document Classifier (Currently feature is not available for GA and needs to be requested via the [form](https://docs.google.com/forms/d/e/1FAIpQLSfDuC9bGyEwnseEYIC3I2LvNjzz-XZ2n1RS4X5pnIk2eSbk3A/viewform))
  - After Project has been whitelisted for using Classifier, navigate to **Document AI -> Workbench**  and select **Custom Document Classifier** -> CREATE PROCESSOR.
  - Create New Labels for each document type you plan to use.  
  - Train Classifier using sample forms to classify the labels.
  - Deploy the new trained version via the UI.
  - Set the new version as default and test it manually via the UI by uploading the test document. is it classified properly?

> If you have just one sample_form.pdf, and you want to use it for classifier, use following utility to copy same form into the gcs bucket, later to use for classification. At least 10 instances are needed (all for Training set).
```shell
utils/copy_forms.sh -f sample_data/<path_to_form>.pdf -d gs://<path_to_gs_uri> -c 10
```

## <a name="system_config"></a>Configuring the System
- Config file is stored in the GCS bucket and dynamically used by the pipeline: `gs://${PROJECT_ID}-config/config.json`


  - For the config changes, download, edit, and upload the  `gs://${PROJECT_ID}-config/config.json` file:

    ```shell
    gsutil cp "gs://${PROJECT_ID}-config/config.json" common/src/common/configs/config.json 
    ```

  - Apply required changes as discussed later in this section. 

  - Upload config:
    ```shell
    gsutil cp common/src/common/configs/config.json "gs://${PROJECT_ID}-config/config.json"

### Adding Classifier 
Since currently Classifier is not in GA and has to be manually created, following section needs to be added inside  `parser_config` to activate Classification step (replace  <PROJECT_ID> and <PROCESSOR_ID> accordingly):

```shell
"parser_config": {
    # ... parsers here ...
    
    "classifier": {
      "location": "us",
      "parser_type": "CUSTOM_CLASSIFICATION_PROCESSOR",
      "processor_id": "projects/<PROJECT_ID>/locations/us/processors/<PROCESSOR_ID>"
    }
  }
```


### Adding Support for Additional Type of Forms

1. Deploy and train the DocAI  processor.


2. After processor is created and deployed, add following entry (replace <parser_name> with the name which best describes the processor purpose)  inside `parser_config`:
```shell
"parser_config": {
    # ... parsers here ...
      
    "<parser_name>": {
      "processor_id": "projects/<PROJECT_ID>/locations/us/processors/<PROCESSOR_ID>"
    }
}
```

3. Add configuration for the document type entry inside `document_types_config`:

```shell
"document_types_config": {
     # ... document configurations here ... 
     
    "<document_type_name>": {
        "doc_type": "supporting_documents",
        "display_name": "<Name of the Form>",
        "classifier_label": "<Label-as-trained>",
        "parser": "<parser_name>"
    }  
}

```
Where:
- **doc_type** - Can be of "application_form" or "supporting_documents".
- **display_name** - Text to be displayed in the UI for the 'Choose Document Type/Class' drop-down when manually Re-Classifying.
- **classifier_label** - As defined in the Classifier when training on the documents.
- **parser** - Parser name as defined in the `parser_config` section.

### General Settings
`settings_config` section currently supports the following parameters:

- `extraction_confidence_threshold` - threshold to mark documents for HITL as *Needs Review*. Compared with the *calculated average* confidence score across all document  labels. 
- `field_extraction_confidence_threshold` - threshold to mark documents for HITL as *Needs Review*. Compared with the *minimum* confidence score across all document labels.
- `classification_confidence_threshold` - threshold to pass Classification step. When the confidence score as returned by the Classifier is less, the default behavior is determined by the `classification_default_class` setting. If the settings is "None" or non-existing document type, document remain *Unclassified*. 
- `classification_default_class` - the default behavior for the unclassified forms (or when classifier is not configured). Needs to be a valid  name of the document type, as configured in the `document_types_config`.


## Cross-Project Setup
If you want to enable cross project access, following steps need to be done manually.

Limitations: Two projects need to be within the same ORG. 
For further reference, lets define the two projects:
- GCP Project to run the Claims Data Activator - Engine (**Project CDA**)
- GCP Project to train and serve Document AI Processors and Classifier  (**Project DocAI**)

1) Inside Project DocAI [add](https://medium.com/@tanujbolisetty/gcp-impersonate-service-accounts-36eaa247f87c) following service account of the Project CDA `gke-sa@{PROJECT_CDA_ID}.iam.gserviceaccount.com` (used for GKE Nodes) and grant following  [roles](https://cloud.google.com/document-ai/docs/access-control/iam-roles):
   - **Document AI Viewer** - To grant access to view all resources and process documents in Document AI
   Where `{PROJECT_CDA_ID}` - to be replaced with the ID of the Project CDA
2) Inside Project CDA grant following permissions to the default Document AI service account of the Project DocAI: `service-{PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com`
   - **Storage Object Viewer** - [To make files in Project CDA accessible to Project DocAI](https://cloud.google.com/document-ai/docs/cross-project-setup) (This could be done on the `${PROJECT_CDA_ID}-document-upload` and `${PROJECT_CDA_ID}-docai-output` bucket level with the forms to handle).
   - **Storage Object Admin**  - To allow DocAI processor to save extracted entities as json files inside `${PROJECT_CDA_ID}-output` bucket of the Project CDA  (This could be done on the `${PROJECT_CDA_ID}-output` bucket level).
   Where `{PROJECT_DOCAI_NUMBER}` - to be replaced with the Number of the Project DocAI

```shell
  gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID --member="serviceAccount:gke-sa@${PROJECT_ID}.iam.gserviceaccount.com"  --role="roles/documentai.viewer"
  PROJECT_DOCAI_NUMBER=$(gcloud projects describe "$DOCAI_PROJECT_ID" --format='get(projectNumber)')
  gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-docai-output --member="serviceAccount:service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com" --role="roles/storage.admin"
  gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-document-upload --member="serviceAccount:service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com" --role="roles/storage.objectViewer"
```
## Rebuild / Re-deploy Microservices

Updated sources from the Git repo:
```shell
git pull
```
The following wrapper script will use skaffold to rebuild/redeploy microservices:
```shell
./deploy.sh
```

You can additionally [clear all existing data (in GCS, Firestore and BigQuery)](#cleaning_data) 


# Utilities
## Prerequisites
Make sure to install all required libraries prior to using utilities listed below: 
```shell
pip3 install -r utils/requirements.tx
```
## Testing Utilities
- Following utility would be handy to list all the entities the Trained processor Could extract from the document:

  ```shell
  export RPOCESSOR_ID=<your_processor_id>
  python utils/gen_config_processor.py -f <my-local-dir>/<my-sample-form>.pdf 
  ```

## <a name="cleaning_data"></a>Cleaning Data

Make sure to first install dependency libraries for utilities:
```shell
pip3 install -r utils/requirements.tx
```

- Following script cleans all document related data (requires PROJECT_ID to be set upfront as an env variable):
  - Firestore `document` collection
  - BigQuery `validation` table
  - `${PROJECT_ID}-pa-forms` bucket
  - `${PROJECT_ID}-document-upload` bucket
  
  ```shell
  utils/cleanup.sh
  ```
  
> Please, note, that due to active StreamingBuffer, BigQuery can only be cleaned after a table has received no inserts for an extended interval of time (~ 90 minutes). Then the buffer is detached and DELETE statement is allowed.
> For more details see [here](https://cloud.google.com/blog/products/bigquery/life-of-a-bigquery-streaming-insert) .

# Configuration Service
Config Service (used by adp ui):
- `http://$API_DOMAIN/config_service/v1/get_config?name=document_types_config`
- `http://$API_DOMAIN/config_service/v1/get_config`

## Deployment Troubleshoot

### Terraform Troubleshoot

#### App Engine already exists
```
│ Error: Error creating App Engine application: googleapi: Error 409: This application already exists and cannot be re-created., alreadyExists
│
│   with module.firebase.google_app_engine_application.firebase_init,
│   on ../../modules/firebase/main.tf line 3, in resource "google_app_engine_application" "firebase_init":
│    3: resource "google_app_engine_application" "firebase_init" {
```

**Solution**: Import the existing project in Terraform:
```
cd terraform/environments/dev
terraform import module.firebase.google_app_engine_application.firebase_init $PROJECT_ID

```

### CloudRun Troubleshoot

The CloudRun service “queue” is used as the task dispatcher from listening to Pub/Sub “queue-topic”
- Go to CloudRun logging to see the errors

### Frontend Web App

- When opening up the ADP UI for the first time, you’ll see the HTTPS not secure error, like below:
```
Your connection is not private
```

- Open the chrome://net-internals/#hsts in URL, and delete the domain HSTS.
- (Optional) Click the “Not Secure” icon on the top, and select the “Certificate is not valid” option, and select “Always Trust”.


# Development

### Prerequisites

Install required packages:

- For MacOS:
  ```
  brew install --cask skaffold kustomize google-cloud-sdk
  ```

- For Windows:
  ```
  choco install -y skaffold kustomize gcloudsdk
  ```

* Make sure to use __skaffold 1.24.1__ or later for development.

### Initial setup for local development
After cloning the repo, please set up for local development.

* Export GCP project id and the namespace based on your Github handle (i.e. user ID)
  ```
  export PROJECT_ID=<Your Project ID>
  export SKAFFOLD_NAMESPACE=<Replace with your Github user ID>
  export REGION=us-central1
  ```
* Log in gcloud SDK:
  ```
  gcloud auth login
  ```
* Run the following to set up critical context and environment variables:
  ```
  ./setup/setup_local.sh
  ```
  This shell script does the following:
  - Set the current context to `gke_autodocprocessing-demo_us-central1_default_cluster`. The default cluster name is `default_cluster`.
    > **IMPORTANT**: Please do not change this context name.
  - Create the namespace $SKAFFOLD_NAMESPACE and set this namespace for any further kubectl operations. It's okay if the namespace already exists.

### Build and run all microservices in the default GKE cluster

> **_NOTE:_**  By default, skaffold builds with CloudBuild and runs in GKE cluster, using the namespace set above.

To build and run in cluster:
```
skaffold run --port-forward
```

### Build and run all microservices in Develompent mode with live reload

To build and run in cluster with hot reload:
```
skaffold dev --port-forward
```
- Please note that any change in the code will trigger the build process.

### Build and run with a specific microservice

```
skaffold run --port-forward -m <Microservice>
```

You can also run multiple specific microservices altogether. E.g.:

```
skaffold run --port-forward -m sample-service,other-service
```

### Build and run microservices with a custom Source Repository path
```
skaffold dev --default-repo=<Image registry path> --port-forward
```

E.g. you can point to a different GCP Cloud Source Repository path:
```
skaffold dev --default-repo=gcr.io/another-project-path --port-forward
```

### Run with local minikube cluster

Install Minikube:

```
# For MacOS:
brew install minikube

# For Windows:
choco install -y minikube
```

Make sure the Docker daemon is running locally. To start minikube:
```
minikube start
```
- This will reset the kubectl context to the local minikube.

To build and run locally:
```
skaffold run --port-forward

# Or, to build and run locally with hot reload:
skaffold dev --port-forward
```

Optionally, you may want to set `GOOGLE_APPLICATION_CREDENTIALS` manually to a local JSON key file.
```
GOOGLE_APPLICATION_CREDENTIALS=<Path to Service Account key JSON file>
```

### Deploy to a specific GKE cluster

> **IMPORTANT**: Please change gcloud project and kubectl context before running skaffold.

Replace the `<Custom GCP Project ID>` with a specific project ID and run the following:
```
export PROJECT_ID=<Custom GCP Project ID>

# Switch to a specific project.
gcloud config set project $PROJECT_ID

# Assuming the default cluster name is "default_cluster".
gcloud container clusters get-credentials default_cluster --zone us-central1-a --project $PROJECT_ID
```

Run with skaffold:
```
skaffold run -p custom --default-repo=gcr.io/$PROJECT_ID

# Or run with hot reload and live logs:
skaffold dev -p custom --default-repo=gcr.io/$PROJECT_ID
```

### Build and run microservices with a different Skaffold profile
```
# Using custom profile
skaffold dev -p custom --port-forward

# Using prod profile
skaffold dev -p prod --port-forward
```

### Skaffold profiles

By default, the Skaffold YAML contains the following pre-defined profiles ready to use.

- **dev** - This is the default profile for local development, which will be activated automatically with the Kubectl context set to the default cluster of this GCP project.
- **prod** - This is the profile for building and deploying to the Prod environment, e.g. to a customer's Prod environment.
- **custom** - This is the profile for building and deploying to a custom GCP project environments, e.g. to deploy to a staging or a demo environment.

### Useful Kubectl commands

To check if pods are deployed and running:
```
kubectl get po

# Or, watch the live update in a separate terminal:
watch kubectl get po
```

To create a namespace:
```
kubectl create ns <New namespace>
```

To set a specific namespace for further kubectl operations:
```
kubectl config set-context --current --namespace=<Your namespace>
```

## Code Submission Process

### For the first-time setup:
* Create a fork of a Git repository
  - Go to the specific Git repository’s page, click Fork at the right corner of the page:
* Choose your own Github profile to create this fork under your name.
* Clone the repo to your local computer. (Replace the variables accordingly)
  ```
  cd ~/workspace
  git clone git@github.com:$YOUR_GITHUB_ID/$REPOSITORY_NAME.git
  cd $REPOSITORY_NAME
  ```
  - If you encounter permission-related errors while cloning the repo, follow [this guide](https://docs.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) to create and add an SSH key for Github access (especially when checking out code with git@github.com URLs)
* Verify if the local git copy has the right remote endpoint.
  ```
  git remote -v
  # This will display the detailed remote list like below.
  # origin  git@github.com:jonchenn/$REPOSITORY_NAME.git (fetch)
  # origin  git@github.com:jonchenn/$REPOSITORY_NAME.git (push)
  ```

  - If for some reason your local git copy doesn’t have the correct remotes, run the following:
    ```
    git remote add origin git@github.com:$YOUR_GITHUB_ID/$REPOSITORY_NAME.git
    # or to reset the URL if origin remote exists
    git remote set-url origin git@github.com:$YOUR_GITHUB_ID/$REPOSITORY_NAME.git
    ```

* Add the upstream repo to the remote list as **upstream**.
  ```
  git remote add upstream git@github.com:$UPSTREAM_REPOSITORY_NAME.git
  ```
  - In default case, the $UPSTREAM_REPOSITORY_NAME will be the repo that you make the fork from.


### When making code changes

* Sync your fork with the latest commits in upstream/master branch. (more info)
  ```
  # In your local fork repo folder.
  git checkout -f master
  git pull upstream master
  ```

* Create a new local branch to start a new task (e.g. working on a feature or a bug fix):
  ```
  # This will create a new branch.
  git checkout -b feature_xyz
  ```

* After making changes, commit the local change to this custom branch and push to your fork repo on Github. Alternatively, you can use editors like VSCode to commit the changes easily.
  ```
  git commit -a -m 'Your description'
  git push
  # Or, if it doesn’t push to the origin remote by default.
  git push --set-upstream origin $YOUR_BRANCH_NAME
  ```
  - This will submit the changes to your fork repo on Github.

* Go to your Github fork repo web page, click the “Compare & Pull Request” in the notification. In the Pull Request form, make sure that:
  - The upstream repo name is correct
  - The destination branch is set to master.
  - The source branch is your custom branch. (e.g. feature_xyz in the example above.)
  - Alternatively, you can pick specific reviewers for this pull request.

* Once the pull request is created, it will appear on the Pull Request list of the upstream origin repository, which will automatically run tests and checks via the CI/CD.

* If any tests failed, fix the codes in your local branch, re-commit and push the changes to the same custom branch.
  ```
  # after fixing the code…
  git commit -a -m 'another fix'
  git push
  ```
  - This will update the pull request and re-run all necessary tests automatically.
  - If all tests passed, you may wait for the reviewers’ approval.

* Once all tests pass and get approvals from reviewer(s), the reviewer or Repo Admin will merge the pull request back to the origin master branch.

### (For Repo Admins) Reviewing a Pull Request
For code reviewers, go to the Pull Requests page of the origin repo on Github.

* Go to the specific pull request, review and comment on the request.
branch.
* Alternatively, you can use Github CLI `gh` to check out a PR and run the codes locally: https://cli.github.com/manual/gh_pr_checkout
* If all goes well with tests passed, click Merge pull request to merge the changes to the master.

Test for PR changes

### (For Developers) Microservices Assumptions
* app_registration_id used on the ui is referred as case_id in the API code
* case_id is referred as external case_id in the firestore

## Troubleshooting Commands
```shell
terraform destroy -target=module.ingress
```

```shell
helm ls -n ingress-nginx
```

```shell
helm history ingress-nginx -n ingress-nginx
```

```shell
terraform state list
terraform state rm <...>

```