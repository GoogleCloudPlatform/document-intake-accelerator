# Claims Data Activator (CDA)
- [Introduction](#introduction)
  * [Key features](#key-features)
  * [How To Use This Repo](#how-to-use-this-repo)
- [Quick Start](#quick-start)
  * [Prerequisites](#prerequisites)
    + [Projects Creation](#project-creation)
    + [Classifier/Splitter Access](#classifier-splitter-access)
    + [Domain Name Registration](#domain-name-registration)
    + [Installation Using Cloud Shell](#installation-using-cloud-shell)
  * [Preparations](#preparations)
    + [Reserving External IP](#reserving-external-ip)
    + [Private vs Public End Point](#private-vs-public-end-point)
    + [When deploying using Shared VPC](#when-deploying-using-shared-vpc)
    + [Register Cloud Domain](#register-cloud-domain)
    + [Configure DNS `A` record for your domain with IP address reserved above](#configure-dns-record)
    + [Environment Variables](#environment-variables)
  * [Installation](#installation)
    + [Terraform](#terraform)
    + [Front End Config](#front-end-config)
    + [Enable Firebase Auth](#enable-firebase-auth)
    + [Deploy microservices](#deploy-microservices)
  * [(Optional) IAP setup](#iap-setup)
    + [IAP With External identity](#iap-with-external-identity)
- [Configuration](#configuration)
  * [Setting up CDE and CDS](#setting-up-cde-and-cds)
    + [Custom Document Extractor](#custom-document-extractor)
    + [Custom Document Classifier](#custom-document-classifier)
  * [Configuring the System](#configuring-the-system)
    + [Adding Classifier](#adding-classifier)
    + [Adding Support for Additional Type of Forms](#adding-support-for-additional-type-of-forms)
    + [General Settings](#general-settings)
  * [Cross-Project Setup](#cross-project-setup)
  * [Setting-Up Document AI Warehouse](#setting-up-document-ai-warehouse)
- [CDA Usage](#cda-usage)
  * [When Using Private Access](#when-using-private-access)
  * [Out of the box Demo Flow](#out-of-the-box-demo-flow)
    + [Working from the UI](#working-from-the-ui)
    + [Triggering pipeline in a batch mode](#triggering-pipeline-in-a-batch-mode)
- [HITL](#hitl)
- [Rebuild / Re-deploy Microservices](#rebuild-redeploy-microservices)
- [Utilities](#utilities)
  * [Prerequisites](#prerequisites-1)
  * [Testing Utilities](#testing-utilities)
  * [Cleaning Data](#cleaning-data)
  * [Configuration Service](#configuration-service)
  * [Splitter](#splitter)
- [Deployment Troubleshoot](#deployment-troubleshoot)
  * [Checking SSL certificates](#checking-ssl-certificates)
  * [Terraform Troubleshoot](#terraform-troubleshoot)
    + [App Engine already exists](#app-engine-already-exists)
  * [CloudRun Troubleshoot](#cloudrun-troubleshoot)
  * [Frontend Web App](#frontend-web-app)
  * [Troubleshooting Commands](#troubleshooting-commands)
- [CDA Troubleshoot](#cda-troubleshoot)
- [Development Guide](#development-guide)

# Introduction
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

# Quick Start

For a Quick Start and Demo Guide refer to the [Workshop Lab1](docs/Lab1.md), that explains how to install CDA engine with a public external end point. 
Use this README.md to explore in-depth customizations and installation options if needed.

For **DocAI Warehouse utilities**, check [here](utils/docai-wh/README.md).


## Prerequisites

### Project Creation
It is recommended to deploy into two projects: one for the CDA Pipeline Engine (`PROJECT_ID`), and another for the Document AI processors (`DOCAI_PROJECT_ID`). Both projects need to belong to the same Org.
When following this  practice, before deployment create two projects and note down.

### <a name="classifier-splitter-access"></a> Classifier/Splitter Access
Custom Document Classifier and Custom Document Splitter are currently in Preview.
Early access can be granted using this [form](https://docs.google.com/forms/d/e/1FAIpQLSc_6s8jsHLZWWE0aSX0bdmk24XDoPiE_oq5enDApLcp1VKJ-Q/viewform), so that Project is whitelisted.

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

From the Cloud Shell, reserve external global ip named `cda-ip`:
```shell
export PROJECT_ID=
``` 
```shell
gcloud config set project $PROJECT_ID
gcloud services enable compute.googleapis.com
gcloud compute addresses create cda-ip  --global
```

To see the reserved IP:
```shell
gcloud compute addresses describe cda-ip --global
```

Copy terraform sample variable file as `terraform.tfvars`:
 ```shell
cp terraform/stages/foundation/terraform.sample.tfvars terraform/stages/foundation/terraform.tfvars
vi terraform/stages/foundation/terraform.tfvars
```

Verify `cda_external_ip` points to the reserved External IP name inside `terraform/stages/foundation/terraform.tfvars`:
 ```
 cda_external_ip = "cda-ip"   #IP-ADDRESS-NAME-HERE
 ```

### Private vs Public End Point
You have an option to expose UI externally in public internet, or make it fully internal within the internal network.
When exposed, the end point (via domain name) will be accessible via Internet and protected by Firebase Authentication and optionally IAP, enforced
on all the end points.
When protected, you will need machine in the same internal network in order to access the UI (for testing, you could create Windows VM in the same network and access it via RDP using IAP tunnel).

By default, the end-point is private (so then when upgrading customer accidentally end point does not become open unintentionally).
The preference can be set in `terraform/stages/foundation/terraform.tfvars` file via `cda_external_ui` parameter:

```shell
cda_external_ui = false       # Expose UI to the Internet: true or false
```

For simple demo purposes you probably want to expose the end point (`cda_external_ui = true`).

### When deploying using Shared VPC
As is often the case in real-world configurations, this blueprint accepts as input an existing [Shared-VPC](https://cloud.google.com/vpc/docs/shared-vpc)
via the `network_config` variable inside [terraform.tfvars](terraform/stages/foundation/terraform.sample.tfvars).
Follow [these steps](docs/SharedVPC_steps.md) to prepare environment with VPC Host Project and Service project.

- Edit `terraform/stages/foundation/terraform.tfvars` in the editor,
- uncomment `network_config` and fill in required parameters inside `network_config` (when using the [steps above](docs/SharedVPC_steps.md),
- only need to set `HOST_PROJECT_ID`, all other variables are pre-filled correctly):
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

For example, if you have already one CDA installation in your shared vpc and want a second installation, you should manually set master_ipv4_cidr_block to avoid conflicts:
 ```shell
master_ipv4_cidr_block =172.16.16.0/28
 ```

### Register Cloud Domain
Enable Cloud Dns api and Cloud domain APIs:

```shell
gcloud services enable dns.googleapis.com
gcloud services enable domains.googleapis.com
```

Via [Cloud Domain](https://console.cloud.google.com/net-services/domains/registrations) register domain name
(pick desired name and fill in the forms).


### <a name="configure-dns-record"> </a> Configure DNS `A` record for your domain with IP address reserved above
For this step you will need a registered Cloud Domain.
You can use gcloud command to get information about reserved address.
```shell
gcloud compute addresses describe cda-ip --global
```

- Go to [Cloud DNS](https://console.cloud.google.com/net-services/dns/zones) after registering Cloud Domain.
- Create a DNS record set of type A and point to the reserved external IP:
  - On the Zone details page, click on zone name (will be created by the previous step, after registering Cloud Domain).
  - Add record set.
  - Select A from the Resource Record Type menu.
- For IPv4 Address, enter the external IP address that has been reserved.

Once configured, verify that your domain name resolves to the reserved IP address.

  ```bash
  $ nslookup -query=a mydomain.com
  ...(output omitted)..

  ```


### Environment Variables
```shell
export API_DOMAIN=<YOUR_DOMAIN>
export PROJECT_ID=<GCP Project ID to host CDA Pipeline Engine>
```

Optionally, when deploying processors to a different Project, you can set `DOCAI_PROJECT_ID`.
However, If you are deploying CDA engine and already have DOCAI project setup and
running as a result from the previous installation, DO NOT set `DOCAI_PROJECT_ID` variable and leave it blank.
Otherwise, terraform will fail, since it will try to create resources, which already were provisioned (and are owned by a different terraform run).

```shell
export DOCAI_PROJECT_ID=<GCP Project ID to host Document AI processors> #
```


## Installation
### Terraform Foundation

> If you are missing `~/.kube/config` file on your system (never run `gcloud cluster get-credentials`), you will need to modify terraform file.
>
> If following command does not locate a file:
> ```shell
> ls ~/.kube/config
> ```
>
> Uncomment Line 55 in `terraform/stages/foundation/providers.tf` file:
> ```shell
>  load_config_file  = false  # Uncomment this line if you do not have .kube/config file
> ```


Run **init** step to provision required resources in GCP (will run terraform apply with auto-approve):
```shell
bash -e ./init_foundation.sh
```
This command will take **~15 minutes** to complete.
After successfully execution, you should see line like this at the end:

```shell
<...> Completed! Saved Log into /<...>/init_foundation.log
```

> If Cloud shell times out during the operation, a workaround is to use `nohup` command to make sure a command does not exit when Cloud Shell times out.
>
>  ```shell
>  nohup bash -c "time ./init_foundation.sh" &
>  tail -f nohup.out
>  ```

### Front End Config

Run following command to propagate front end with the Domain name and Project ID (this will set REACT_APP_BASE_URL to `https://<your_domain_name>` and PROJECT_ID to your Project ID):
```shell
sed 's|PROJECT_ID|'"$PROJECT_ID"'|g; s|API_DOMAIN|'"$API_DOMAIN"'|g; ' microservices/adp_ui/.sample.env > microservices/adp_ui/.env
```

Edit `microservices/adp_ui/.env` and chose between `http` and `https` protocol depending on internal vs external ui configuration you have selected above:
**Important!!!**
* When not exposing UI externally (`cda_external_ui = false`), REACT_APP_BASE_URL needs to use `http://` Protocol (e.g. **http**://mydomain.com)
* When exposing UI externally (`cda_external_ui = true`), REACT_APP_BASE_URL needs to use `https://` Protocol (e.g. **https**://mydomain.com)

### Enable Firebase Auth
- Before enabling firebase, make sure [Firebase Management API](https://console.cloud.google.com/apis/api/firebase.googleapis.com/metrics) should be disabled in GCP API & Services.
- Go to [Firebase Console UI](https://console.firebase.google.com/) to add your existing project. Select “Pay as you go” and Confirm plan.
- On the left panel of Firebase Console UI, go to Build > Authentication, and click Get Started.
- Select Email/Password as a Sign in method and click Enable.
- Go to users and add email/password for a valid Sign in method.
  [//]: # (- Enable Google auth provider, and select Project support email to your admin’s email. Leave the Project public-facing name as-is. Then click Save.)
- Go to Settings > Authorized domain, add the following to the Authorized domains:
  - Web App Domain (e.g. adp-dev.cloudpssolutions.com).
- Go to Project Overview > Project settings, copy  `Web API Key` you will use this info in the next step.
- In the codebase, open up microservices/adp_ui/.env in an Editor (e.g. `vi`), and change the following values accordingly.
  - REACT_APP_FIREBASE_API_KEY=`Web API Key copied above`
  - REACT_APP_BASE_URL:
    - `http://you-domain.com` for Internal UI
    - `https://you-domain.com` for External UI
  - (Optional) REACT_APP_MESSAGING_SENDER_ID - Google Analytics ID, only available when you enabled the GA with Firebase.
    - You can find this ID in the Project settings > Cloud Messaging

### Enable Identity Platform
- Enable Identity Platform via [Cloud Shell](https://console.cloud.google.com/marketplace/details/google-cloud-platform/customer-identity)
  - It will ask your confirmation to perform Firebase Upgrade and will import all Firebase settings.

 
### Deploy microservices

[//]: # (With kustomize 5.0 there are breaking changes on passing the environment variables.)

[//]: # (While we are making solution to account for those changes and work with kustomize 5.0, as a temporal workaround, please be sure to downgrade to 4.5.7 version when using Cloud Shell:)

[//]: # (```shell)

[//]: # (kustomize version)

[//]: # (sudo rm /usr/local/bin/kustomize)

[//]: # (curl -Lo install_kustomize "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" && chmod +x install_kustomize)

[//]: # (sudo ./install_kustomize 4.5.7 /usr/local/bin)

[//]: # (kustomize version)

[//]: # (```)

Build/deploy microservices (using skaffold + kustomize):
```shell
./deploy.sh
```
This command will take **~10 minutes** to complete, and it will take another **10-15 minutes** for ingress to get ready.  

### Terraform Ingress

Now, when foundation is there and services are deployed, we could deploy Ingress and managed Certificate:

bash -e ./init_ingress.sh

After successfully execution, you should see line like this at the end:

```shell
<...> Completed! Saved Log into /<...>/init_ingress.log
```

You could check status of ingress by either navigating using Cloud Shell to
[GKE Ingress](https://console.cloud.google.com/kubernetes/ingress/us-central1/main-cluster/default/external-ingress/details) and waiting till it appears as solid green.

Or by running following command making sure ingress has the external ip address assigned under `ADDRESS`:

```shell
kubectl get ingress
```
Output:
```text
NAME               CLASS    HOSTS                 ADDRESS         PORTS   AGE
external-ingress   <none>   your_api_domain.com   xx.xx.xxx.xxx   80      140m
```

When ingress is ready, make sure the cert is in the `Active` status. If it shows as `Provisioning`, give it another 5-10 minutes and re-check:
```shell
kubectl describe managedcertificate
```

```text
Status:
  Certificate Name:    mcrt-de87364c-0c03-4dd8-ac37-c33a29fc94fe
  Certificate Status:  Active
  Domain Status:
    Domain:     your_api_domain.com
    Status:     Active

```

## <a name="iap-setup"></a>(Optional) IAP setup

Optionally, it is possibly to enable [IAP](https://cloud.google.com/iap/docs/enabling-kubernetes-howto) to protect all the backend services.
Make sure that if you already have created [oAuth Consent screen](https://console.cloud.google.com/apis/credentials/consent), it is marked as Internal type.


Make sure Env variables are set:
```shell
export PROJECT_ID=
```

Run following script to enable IAP:
```shell
bash -e iap/enable_iap.sh
```

Run following command to disable IAP:
```shell
bash -e iap/disable_iap.sh
```

### IAP With External identity
When not using GCP identity for IAP, following steps to be executed:

1. Modify `Domain restricted sharing` [Org Policy](https://console.cloud.google.com/iam-admin/orgpolicies/) and make it to _Allow All_
2. Go to [oAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent) and make **User type**  _External_
3. [Create google group](https://groups.google.com/my-groups) and add required members to it.
4. [Grant](https://console.cloud.google.com/iam-admin/iam) `IAP-secured Web-App User` Role to the newly created google group as the Principal

#### Errors
When getting error:
```
Access blocked: CDA Application can only be used within its organization
```

Make sure that steps 1 and 2 above are executed.

# Configuration
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

## Configuring the System
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
        "doc_type": {
          "default": "Non-urgent",
          "rules": [
            {
              "ocr_text": "urgent",
              "name": "Urgent-Generic"
            }
          ]
        },
        "display_name": "<Name of the Form>",
        "classifier_label": "<Label-as-trained>",
        "parser": "<parser_name>"
    }  
}

```

```shell
"document_types_config": {
     # ... document configurations here ... 
     
    "<document_type_name>": {
        "doc_type": {
          "default": "Non-urgent",
          "rules": [
            {
              "entities": {
                "name": "reviewTypeUrgent",
                "value": true
              },
              "name": "Urgent-PA"
            }
          ]
        },
        "display_name": "<Name of the Form>",
        "classifier_label": "<Label-as-trained>",
        "parser": "<parser_name>"
    }  
}

```
Where:
- **doc_type** - Specifies rules for type detection (could be based on OCR text or on entity key_name/value)
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

### Introduction
For further reference, lets define the two projects:
- GCP Project to run the Claims Data Activator - Engine (**Project CDA**) => Corresponds to `PROJECT_ID`
- GCP Project to train and serve Document AI Processor  (**Project DocAI**) => Corresponds to `DOCAI_PROJECT_ID`

```shell
export PROJECT_ID=
export DOCAI_PROJECT_ID=
```

To enable cross project access, following permissions need to be granted retrospectively:
1) Inside Project DocAI [add](https://medium.com/@tanujbolisetty/gcp-impersonate-service-accounts-36eaa247f87c) following service account of the Project CDA `gke-sa@$PROJECT_ID.iam.gserviceaccount.com` (used for GKE Nodes) and grant following  [roles](https://cloud.google.com/document-ai/docs/access-control/iam-roles):
- **Document AI Viewer** - To grant access to view all resources and process documents in Document AI.
2) Inside Project CDA grant following permissions to the default Document AI service account of the Project DocAI: `service-{PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com`
- **Storage Object Viewer** - [To make files in Project CDA accessible to Project DocAI](https://cloud.google.com/document-ai/docs/cross-project-setup) (This could be done on the `${PROJECT_ID}-document-upload`).
- **Storage Object Admin**  - To allow DocAI processor to save extracted entities as json files inside `${PROJECT_ID}-docai-output` bucket of the Project CDA  (This could be done on the `${PROJECT_ID}-docai-output` bucket level).
  Where `{PROJECT_DOCAI_NUMBER}` - to be replaced with the Number of the `Project DocAI`.

### Same Organizational Setup (Only)
When both projects are within organization, following steps to be executed:

* Setting of the environment variables:

```shell
export DOCAI_PROJECT_ID=
export PROJECT_ID=
```

* Running a utility script:
```shell
./setup/setup_docai_access.sh
```

### Two different Organizations - Cross Organization Setup (Only)
When two projects are under different organizations, additional steps are required.

#### Reset Organization Policy for Domain restricted sharing
This step is only required when two `Project CDA` and `Project DocAI` do not belong to the same organization.
In that case following policy constraint `constraints/iam.allowedPolicyMemberDomain` needs to be modified for both of them and be set to  `Allowed All`.


Go to GCP Cloud Shell of `PROJECT_ID`:
```shell
export PROJECT_ID=
gcloud services enable orgpolicy.googleapis.com
gcloud org-policies reset constraints/iam.allowedPolicyMemberDomains --project=$PROJECT_ID
```

To verify changes:
```shell
gcloud resource-manager org-policies list --project=$PROJECT_ID
```
Sample output:
```shell
CONSTRAINT: constraints/iam.allowedPolicyMemberDomains
LIST_POLICY: SET
BOOLEAN_POLICY: -
ETAG: CMiArKIGENi33coC
```

Go to GCP Cloud Shell of `DOCAI_PROJECT_ID`:
```shell
export DOCAI_PROJECT_ID=
gcloud org-policies reset constraints/iam.allowedPolicyMemberDomains --project=$DOCAI_PROJECT_ID
```


[//]: # (Alternatively, changing of organization Policy could be done via UI.)

[//]: # (In order to do so, go to Cloud Console  IAM-> [Organization Policies]&#40;https://console.cloud.google.com/iam-admin/orgpolicies/list&#41; and find `constraints/iam.allowedPolicyMemberDomain` which refers to Domain restricted sharing.)

[//]: # ()
[//]: # (**Select `Manage policy` Icon**:)

[//]: # (* Applies to: => Customize)

[//]: # (* Policy Enforcement => Replace )

[//]: # (* Add rule => `Allow All`)

[//]: # ()
[//]: # (**and submit Save**)

[//]: # ()
[//]: # (Perform step above for both `Project DocAI` and `Project CDA`.)

### Grant Required permissions to DocAI Project

#### Option 1 - using service account
After modifying Organization Policy constraint, go to `Project DocAI` Console Shell and run following commands:
* Set env variables accordingly:
```shell
  export PROJECT_ID=
  export DOCAI_PROJECT_ID=
  gcloud config set project $DOCAI_PROJECT_ID
```
* Execute following commands to grant permissions:
```shell
  gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID --member="serviceAccount:gke-sa@${PROJECT_ID}.iam.gserviceaccount.com"  --role="roles/documentai.apiUser"
  gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID --member="serviceAccount:gke-sa@${PROJECT_ID}.iam.gserviceaccount.com"  --role="roles/documentai.viewer"
  PROJECT_DOCAI_NUMBER=$(gcloud projects describe "$DOCAI_PROJECT_ID" --format='get(projectNumber)')
  echo PROJECT_DOCAI_NUMBER=$PROJECT_DOCAI_NUMBER
```
* Copy PROJECT_DOCAI_NUMBER from the output above

### Option 1 - using managed Group (Alternative)
Alternatively, you could create a group in the Organization of DOCAI_PROJECT, grant permissions to the group and assign members to that group.

* Create a user group, that allows external users (later referred as `GROUP_EMAIL`) in the DocAI Project organization.

* Set env variables accordingly:
```shell
  export PROJECT_ID=
  export DOCAI_PROJECT_ID=
  export GROUP_EMAIL=
  gcloud config set project $DOCAI_PROJECT_ID
```

* Execute following commands to grant permissions:
```shell
gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
--member="group:${GROUP_EMAIL}" \
--role="roles/documentai.apiUser"
gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
--member="group:${GROUP_EMAIL}" \
--role="roles/documentai.viewer"
```

* Add member to the group:
```shell
gcloud identity groups memberships add --group-email="${GROUP_EMAIL}" --member-email="serviceAccount:gke-sa@${PROJECT_ID}.iam.gserviceaccount.com" --roles=MEMBER
```

### Grant Required permissions to CDA engine Project
Go to `Project CDA` Console Shell and run following commands:
* Set env variables accordingly:
```shell
  export PROJECT_ID=
  export DOCAI_PROJECT_ID=
  export PROJECT_DOCAI_NUMBER=
  gcloud config set project $PROJECT_ID
```
* Execute following commands:
```shell
  gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-docai-output --member="serviceAccount:service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com" --role="roles/storage.admin"
  gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-document-upload --member="serviceAccount:service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com" --role="roles/storage.objectViewer"
```

## Setting-Up Document AI Warehouse

### Create document_schema, folder_schema and folder
You could use either existing PROJECT_ID or create a separate standlone project for the Document Ai Warehouse (recommended).

- Enable [Document AI Warehouse API](https://pantheon.corp.google.com/apis/library/contentwarehouse.googleapis.com) in your Google Cloud project and click Next.
```shell
  gcloud services enable contentwarehouse.googleapis.com
```
- Provision the Instance:
  - For now, use `Universal Access: No document level access control` for the ACL modes in DocAI Warehouse and click Provision, then Next.
  - Provision DocAI warehouse Instance [Document AI Warehouse console](https://documentwarehouse.cloud.google.com) (which is external to the Google Cloud console).
  - You can skip Optional step for Service Account creation  and click Next
  - Click Done
- Follow link to Configure the Web Application: 
  - Select Location ( same as the location of the CDA and DocAI processors)
  - Click Done
- [Create document_schema](https://codelabs.developers.google.com/codelabs/docai-warehouse#4) 
  - This will be an empty schema without any additional properties
  - Note down schema_id => you will use schema_id in the `config.json` file
- Create folder_schema
  - Go to "Admin" -> Schema -> Add new -> Schema Type = Folder
  - This will be an empty schema without any additional properties
- Crate folder using previously created folder_schema:
  - Add New -> Create a new Folder
    - Note down folder id => you will use folder_id in the `config.json` file

#### When using a dedicated Project for Document AI Warehouse 
For cross-organizations only: 
* Modify  policy constraint inside the Argolis to allow cross org access:
  ```shell
  export PROJECT_ID=
  gcloud services enable orgpolicy.googleapis.com
  gcloud org-policies reset constraints/iam.allowedPolicyMemberDomains --project=$PROJECT_ID
  ```

* Grant accesses for DocAI Warehouse service account to the Cloud Storage for view/write access:
```shell
  export DOCAI_WH_PROJECT_ID=
  export DOCAI_WH_PROJECT_NUMBER=$(gcloud projects describe ${DOCAI_WH_PROJECT_ID} --format='get(projectNumber)')
  echo DOCAI_WH_PROJECT_NUMBER=${DOCAI_WH_PROJECT_NUMBER}
  gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-docai-output --member="serviceAccount:service-${DOCAI_WH_PROJECT_NUMBER}@gcp-sa-cloud-cw.iam.gserviceaccount.com" --role="roles/storage.objectViewer"
  gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-document-upload --member="serviceAccount:service-${DOCAI_WH_PROJECT_NUMBER}@gcp-sa-cloud-cw.iam.gserviceaccount.com" --role="roles/storage.objectViewer"
```

* Grant following roles to the GKE Service Account inside Warehouse Project:
```shell
  gcloud projects add-iam-policy-binding $DOCAI_WH_PROJECT_ID --member="serviceAccount:gke-sa@${PROJECT_ID}.iam.gserviceaccount.com"  --role="roles/documentai.apiUser"
  gcloud projects add-iam-policy-binding $DOCAI_WH_PROJECT_ID --member="serviceAccount:gke-sa@${PROJECT_ID}.iam.gserviceaccount.com"  --role="roles/contentwarehouse.documentAdmin"
```

### Setting up config

Each entity inside `document_types_config` (corresponding to a different supported form type), can have optional Document AI Warehouse integration:
```shell
  "document_types_config": {
    "generic_form": {
      "display_name": "Generic Form",
      "parser": "claims_form_parser",
      "classifier_label": "Generic",
      "doc_type": {
        "default": "Non-urgent",
        "rules": [
          {
            "ocr_text": "urgent",
            "name": "Urgent-Generic"
          }
        ]
      },
      "document_ai_warehouse": {
        "project_number": "DOCAI_WH_PROJECT_NUMBER",
        "folder_id": "FOLDER_ID",
        "document_schema_id": "SCHEMA_ID",
        "api_location": "us"
      }
    },
```


# CDA Usage
## When Using Private Access

- Create Windows VM in the VPC network used to deploy CDA Solution
- Create firewall rules to open up TCP:3389 port for RDP connection
- [Connect to Windows VM using RDP](https://cloud.google.com/compute/docs/instances/connecting-to-windows)
  - OpenUp IAP Tunnel by running following command:

  ```shell
  gcloud compute start-iap-tunnel VM_INSTANCE_NAME 3389     --local-host-port=localhost:3389     --zone=<YOUR_ONE> --project=$PROJECT_ID
  ```


## Out of the box Demo Flow

Quick test to trigger pipeline to parse  the sample form:
```shell
./start_pipeline.sh -d sample_data/bsc_demo/bsc-dme-pa-form-1.pdf  -l demo-batch
```

### Working from the UI
* To access the Application UI, Navigate to Domain Name using the browser and login using username/password created in the previous steps.
* Upload a sample document (e.g. [form.pdf](sample_data/demo/form.pdf))  using *Upload a Document* button.  From *Choose Program* drop-down, select `California` state.
  * Right now, the Form Processor is set up as a default processor (since no classifier is deployed or trained), so each document will be processed with the **Form Parser** and extracted data will be streamed to the BigQuery.
* As you click Refresh Icon on the top right, you will see different Status the Pipeline goes through: *Classifying -> Extracting -> Approved* or *Needs Review*.

* If you select *View* action, you will see the key/value pairs extracted from the Document.

* Navigate to BigQuery and check for the extracted data inside `validation` dataset and `validation_table`.

* You could also run sample query from the Cloud Shell (to output all extracted entities from the form):
  ```shell
  ./sql-scripts/run_query.sh entities
  ```
  
> The setting for the default processor is done through the following configuration setting  "settings_config" -> "classification_default_label".  Explained in details in the [Configuring the System](#configuring-the-system).


### Triggering pipeline in a batch mode
*NB: Currently only pdf documents are supported, so if you have a jpg or png, please first convert it to pdf.*

For example, to trigger pipeline to parse the sample form:
```shell
./start_pipeline.sh -d sample_data/bsc_demo/bsc-dme-pa-form-1.pdf  -l demo-batch
```

> The Pipeline is triggered when an empty file named START_PIPELINE is 
> uploaded to the `${PROJECT_ID}-pa-forms` GCS bucket. When the START_PIPELINE 
> document is uploaded, all `*.pdf` 
> files containing in that folder (including sub-folders) are sent to the processing queue.  
> <br>
> All documents within the same GCS folder are treated as related documents, will become part of same package (will share case_id). Current limitation with that logic is that only one document of certain type could be used. If there are multiple documents of same type, only one is marked active, others are marked as in-active, as if they were a replacement. 
> This is legacy business logic, subject to change in case it really becomes an obstacle.
> <br>
> 
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

# HITL
Using Frontend UI it is possible to review and correct the data extracted by the DocAI.
Documents with low confidence score are marked for the Review Process.

Corrected values are saved to the BigQuery and could be retrieved using sample query:

```shell
export PROJECT_ID=
```
```shell
sql-scripts/run_query.sh corrected_values
```

Sample output:

```shell
+----------------------+--------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------+------------------------------------------------------------+------------+----------------------------------------------------------+
|         uid          |               case_id                |   document_class   |         timestamp          |                                                    gcs_doc_path                                                     |                       corrected_value                       |                           value                            | confidence |                           name                           |
+----------------------+--------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------+------------------------------------------------------------+------------+----------------------------------------------------------+
| uPFanqkU7XgxVs3hmSQ0 | demo02-package_b1ee7248-d954-11ed    | pa_form_texas      | 2023-04-12T18:59:11.154157 | gs://cda-001-engine-document-upload/demo02-package_b1ee7248-d954-11ed/uPFanqkU7XgxVs3hmSQ0/pa-form-1.pdf            | 10672096568                                                 | : 10672096568                                              |          0 | spPhone                                                  |
| uPFanqkU7XgxVs3hmSQ0 | demo02-package_b1ee7248-d954-11ed    | pa_form_texas      | 2023-04-12T18:59:11.154157 | gs://cda-001-engine-document-upload/demo02-package_b1ee7248-d954-11ed/uPFanqkU7XgxVs3hmSQ0/pa-form-1.pdf            | 12441600016                                                 | : 12441600016                                              |          0 | spFax                                                    |
| luDiPU4fuT3IkPPKZsTm | demo01-package_520e0466-d886-11ed    | pa_form_cda        | 2023-04-11T16:36:26.804722 | gs://cda-001-engine-document-upload/demo01-package_520e0466-d886-11ed/luDiPU4fuT3IkPPKZsTm/bsc-dme-pa-form-1.pdf    | Shepherdborough                                             | Shepherdboroughtate                                        |       0.33 | beneficiaryCity                                          |
| U3du4Ujnxz6s10YilVh1 | batch2_9aee5ba4-d999-11ed            | pa_form_cda        | 2023-04-13T04:54:38.711255 | gs://cda-001-engine-document-upload/batch2_9aee5ba4-d999-11ed/U3du4Ujnxz6s10YilVh1/pg4_Prior_Auth_bsc-combined.pdf  | CA                                                          | San Ramon                                                  |       0.35 | beneficiaryState                                         |                               |
| dR7NPclwqQa7fOB3ZD6r | b7050058-d963-11ed-9d35-da2bd0c976e4 | pa_form_texas      | 2023-04-13T15:21:19.771042 | gs://cda-001-engine-document-upload/b7050058-d963-11ed-9d35-da2bd0c976e4/dR7NPclwqQa7fOB3ZD6r/pa-form-test25.pdf    | 0-288-12345-8                                               | 0-288-04411-8                                              |          1 | prevAuthNumber                                           |
| UHcBHasyDTjssIZDK8MF | batch2_9aee5ba4-d999-11ed            | health_intake_form | 2023-04-13T04:57:39.769887 | gs://cda-001-engine-document-upload/batch2_9aee5ba4-d999-11ed/UHcBHasyDTjssIZDK8MF/pg5_bsc_pa_form_bsc-combined.pdf | Sally.walker@cmail.com                                      | Sally, walker@cmail.com                                    |          1 | Email                                                    |cy                                 |
+----------------------+--------------------------------------+--------------------+----------------------------+---------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------+------------------------------------------------------------+------------+----------------------------------------------------------+

```

In order to use this data to uptrain the model:
* Documents to be uploaded to the GCS bucket and imported as a training set for the DocAI model with auto-labeling on.
* An operator to review the BoundingBoxes and fix them appropriately (those uploaded documents will appear as Auto-labeled). Only BoundingBoxes  could be changed/fixed for CDE.
* If text is extracted wrongly due to the OCR, nothing could be done for this model (do not change the text field itself, that info will not be handled by the DocAI).
* Uptrain and deploy new model.

# <a name="rebuild-redeploy-microservices"></a> Rebuild / Re-deploy Microservices

Update sources from the Git repo:
```shell
git pull
```

Set environment variables:
```shell
export PROJECT_ID=<set your project id here>
export API_DOMAIN=<set-api domain here>
```

## Upgrading Infrastructure
In some cases new features/fixes will involve changes to the infrastructure.
In that case you will need to re-run terraform for foundation and ingress: 

```shell
./init_foundation.sh
./init_ingress.sh
```
 
## Deploy microservices

The following wrapper script will use skaffold to rebuild/redeploy microservices:
```shell
./deploy.sh
```

You can additionally [clear all existing data (in GCS, Firestore and BigQuery)](#cleaning-data).


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

## Cleaning Data

Make sure to first install dependency libraries for utilities:
```shell
pip3 install -r utils/requirements.txt
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
> For more details see [here](https://cloud.google.com/blog/products/bigquery/life-of-a-bigquery-streaming-insert).

## Configuration Service
Config Service (used by adp ui):
- `http://$API_DOMAIN/config_service/v1/get_config?name=document_types_config`
- `http://$API_DOMAIN/config_service/v1/get_config`

## Splitter

[Included splitter utility to split the documents](utils/pdf-splitter/README.md).
# Deployment Troubleshoot


## Checking SSL certificates

```shell
gcloud compute ssl-certificates list --global
```

```shell
gcloud compute ssl-certificates describe CERTIFICATE_NAME  --global --format="get(name,managed.status, managed.domainStatus)"
```

```shell
kubectl describe managedcertificate
```

```shell
gcloud compute ssl-policies list
```

```shell
kubectl describe ingress
```

## Terraform Troubleshoot

### App Engine already exists
```
│ Error: Error creating App Engine application: googleapi: Error 409: This application already exists and cannot be re-created., alreadyExists
│
│   with module.firebase.google_app_engine_application.firebase_init,
│   on ../../modules/firebase/main.tf line 3, in resource "google_app_engine_application" "firebase_init":
│    3: resource "google_app_engine_application" "firebase_init" {
```

**Solution**: Import the existing project in Terraform:
```
cd terraform/stages/foundation
terraform import module.firebase.google_app_engine_application.firebase_init $PROJECT_ID

```

## CloudRun Troubleshoot

The CloudRun service “queue” is used as the task dispatcher from listening to Pub/Sub “queue-topic”
- Go to CloudRun logging to see the errors

## Frontend Web App

- When opening up the ADP UI for the first time, you’ll see the HTTPS not secure error, like below:
```
Your connection is not private
```

- Open the chrome://net-internals/#hsts in URL, and delete the domain HSTS.
- (Optional) Click the “Not Secure” icon on the top, and select the “Certificate is not valid” option, and select “Always Trust”.



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

# CDA Troubleshoot

## Errors when using Classifier/Extractor

Such as `400 Error, Failed to process all documents`.
Make sure [Cross Project Access is setup](#cross-project-setup) between DocAI and CDA projects.

Can be resolved by running this script:
```shell
export DOCAI_PROJECT_ID=
export PROJECT_ID=
```

```shell
./setup/setup_docai_access.sh
```


## Classification Service Logs

Search for `Classification prediction` to get summary of the prediction results:

```shell
2023-04-14 17:35:52.542 PDT | Classification predictions for 76983ddc-db25-11ed-90fd-faad96329953_aOA5oKoKS3jszgrQ7rTr_bsc-dme-pa-form-1.pdf
2023-04-14 17:35:52.543 PDT | Classification prediction results: document_class=fax_cover_page with confidence=0.0008332811412401497
2023-04-14 17:35:52.543 PDT | Classification prediction results: document_class=pa_form_texas with confidence=0.0009312000474892557
2023-04-14 17:35:52.543 PDT | Classification prediction results: document_class=pa_form_cda with confidence=0.9972623586654663
2023-04-14 17:35:52.543 PDT | Classification prediction results: document_class=health_intake_form with confidence=0.0009731759782880545
2023-04-14 17:35:53.178 PDT | Classification prediction results: predicted_class=pa_form_cda, predicted_score=0.9972623586654663
```

# Development Guide

For development guide, refer [here](docs/Development.md).

```shell
$npm install -g firebase-tools
firebase --project $PROJECT_ID firestore:delete "/document/*" --recursive --force 
```
