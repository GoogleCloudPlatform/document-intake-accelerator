# Table of contents
<!-- TOC -->
* [Table of contents](#table-of-contents)
  * [About](#about)
  * [Pre-requisites](#pre-requisites)
    * [Create New Project](#create-new-project)
  * [Installation](#installation)
    * [Setting up](#setting-up)
    * [Terraform Foundation](#terraform-foundation)
    * [Front End Config](#front-end-config)
    * [Enable Firebase Auth](#enable-firebase-auth)
    * [Deploy microservices](#deploy-microservices)
    * [Terraform Ingress](#terraform-ingress)
  * [Out of the box UI demo flow](#out-of-the-box-ui-demo-flow)
  * [Human In the Loop (HITL) Demo](#human-in-the-loop--hitl--demo)
  * [Connecting to the existing DocAI processors](#connecting-to-the-existing-docai-processors)
    * [Granting Cross-Org permissions](#granting-cross-org-permissions)
    * [Modifying config.json file](#modifying-configjson-file)
    * [Testing New Configuration](#testing-new-configuration)
  * [Data Visualization](#data-visualization)
  * [Troubleshooting](#troubleshooting)
    * [Ingress cannot get deployed](#ingress-cannot-get-deployed)
    * [ERROR: This site can’t provide a secure](#error--this-site-cant-provide-a-secure)
    * [ERROR: googleapi: Error 400: Master version "1.XX.XX-gke.XXX" is unsupported.](#error--googleapi--error-400--master-version--1xxxx-gkexxx--is-unsupported)
<!-- TOC -->
## About

This is a customized version of installation Guide that installs CDA engine using Public End point and connects to the existing DocAI Processor Project.
For other flavours and more detailed steps, check the original full [README](../README.md).

## Pre-requisites

### Create New Project 
* You will need access the GCP environment and project owner rights.
* Installation will happen in the newly created project.

## Installation
### Setting up

* Get the Git Repo in the Cloud Shell:
```shell
git clone git@github.com:hcls-solutions/claims-data-activator.git
cd claims-data-activator
```

* Set env variable for _PROJECT_ID_:
* 
```shell
export PROJECT_ID=<YOUR_PROJECT_ID>
gcloud config set project $PROJECT_ID
```

* When running from the developer machine, run following commands:

```shell
gcloud auth application-default login
gcloud auth login
gcloud auth application-default set-quota-project $PROJECT_ID
```

* Reserve External IP:
```shell
gcloud services enable compute.googleapis.com
gcloud compute addresses create cda-ip  --global
```

* Note down the reserved IP address:
```shell
gcloud compute addresses describe cda-ip --global
```

Sample output:

```shell
address: 34.xx.xx.xx
addressType: EXTERNAL
creationTimestamp: '2023-04-28T14:31:23.985-07:00'
description: ''
  ...(output omitted)..
```

* Get ready with DNS Domain by enabling APIs:
* 
```shell
gcloud services enable dns.googleapis.com
gcloud services enable domains.googleapis.com
```

* Register a Cloud Domain:
  * Purchase a [Cloud Domain](https://cloud.google.com/domains/docs/overview)  -> Cloud DNS type
    * Navigate to [Cloud Domain](https://console.cloud.google.com/net-services/domains/registrations), pick desired name and fill in the forms:


* Create a DNS record set of `type A` and point to the reserved external IP:
    - On the Zone details page, click on zone name (will be created by the previous step, after registering Cloud Domain).
    - Add record set.
    - Select A from the Resource Record Type menu.
    - For IPv4 Address, enter the external IP address that has been reserved (or can be selected via the UI).


* Set env variable for _API_DOMAIN_ registered:
```shell
export API_DOMAIN=<YOUR_DOMAIN>
````

* Verify that your domain name resolves to the reserved IP address:

```bash
  $ nslookup -query=a $API_DOMAIN
  ...(output omitted)..
``` 

### Terraform Foundation

Copy terraform sample variable file as `terraform.tfvars`:
 ```shell
cp terraform/stages/foundation/terraform.sample.tfvars terraform/stages/foundation/terraform.tfvars
vi terraform/stages/foundation/terraform.tfvars
```

Verify `cda_external_ip` points to the reserved External IP name inside `terraform/stages/foundation/terraform.tfvars`:
 ```
 cda_external_ip = "cda-ip"   #IP-ADDRESS-NAME-HERE
 ```

For quickstart simple demo, you want to change and make end point public (change from `false` to `true`):
```shell
cda_external_ui = true       # Expose UI to the Internet: true or false
```


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

* Run **init** step to provision foundational required resources in GCP, including GKE (will run terraform apply with auto-approve):
```shell
bash -e ./init_foundation.sh
```
This command will take **~15 minutes** to complete.
After successfully execution, you should see line like this at the end:

```shell
<...> Completed! Saved Log into /<...>/init_foundation.log
```

### Front End Config

* Run following command to propagate front end with the Domain name and Project ID (this will set REACT_APP_BASE_URL to `https://<your_domain_name>` and PROJECT_ID to your Project ID):
```shell
sed 's|PROJECT_ID|'"$PROJECT_ID"'|g; s|API_DOMAIN|'"$API_DOMAIN"'|g; ' microservices/adp_ui/.sample.env > microservices/adp_ui/.env
```

### Enable Firebase Auth
- Before enabling firebase, make sure [Firebase Management API](https://console.cloud.google.com/apis/api/firebase.googleapis.com/metrics) should be disabled in GCP API & Services.
- Go to [Firebase Console UI](https://console.firebase.google.com/) to add your existing project. Select “Pay as you go” and Confirm plan.
- On the left panel of Firebase Console UI, go to Build > Authentication, and click Get Started.
- Select Email/Password as a Sign in method and click Enable => Save. Note them down, you will need it to sign in.
- Go to users and add email/password for a valid Sign in method
  - Enable Google auth provider, and select Project support email to your admin’s email. Leave the Project public-facing name as-is. Then click Save.
- Go to Settings > Authorized domain, add the following to the Authorized domains:
  - Web App Domain (e.g. adp-dev.cloudpssolutions.com) - the one registered previously as `API_DOMAIN`
- Go to Project Overview > Project settings, copy  `Web API Key` you will use this info in the next step.

```shell
vi microservices/adp_ui/.env
```
- In the codebase, open up microservices/adp_ui/.env in an Editor (e.g. `vi`), and change the following values accordingly.
```shell
REACT_APP_FIREBASE_API_KEY=`"Web API Key copied above"`
```
### Deploy microservices
Build/deploy microservices (using skaffold + kustomize):
```shell
./deploy.sh
```
This command will take **~10 minutes** to complete, and it will take another **10-15 minutes** for ingress to get ready and for the cert to be provisioned.  

### Terraform Ingress

Now, when foundation is there and services are deployed, we could deploy Ingress and managed Certificate:

```shell
bash -e ./init_ingress.sh
```

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
  Certificate Status:  Provisioning
  Domain Status:
    Domain:  your_api_domain.com
    Status:  Provisioning
```

```text
Status:
  Certificate Name:    mcrt-de87364c-0c03-4dd8-ac37-c33a29fc94fe
  Certificate Status:  Active
  Domain Status:
    Domain:     your_api_domain.com
    Status:     Active
```

## Out of the box UI demo flow
This relies on the available out-of-the box Form parser.

* To access the Application UI, Navigate to Domain Name using the browser and login using username/password created in the previous steps.
* Upload a sample document (e.g. [form.pdf](../sample_data/demo/form.pdf))  using *Upload a Document* button.  From *Choose Program* drop-down, select `California` state.
  * Right now, the Form Processor is set up as a default processor (since no classifier is deployed or trained), so each document will be processed with the **Form Parser** and extracted data will be streamed to the BigQuery.
* As you click Refresh Icon on the top right, you will see different Status the Pipeline goes through: *Classifying -> Extracting -> Approved* or *Needs Review*.

* If you select *View* action, you will see the key/value pairs extracted from the Document. 

* Click on the Field text box (on the Right under the Extraction Score Column) and a Bounding Box will appear on the Form, showing Location of the Label and extracted value.


* You will notice the form appears as Non-urgent type, now try uploading an urgent form (that has anywhere `Urgent` mark) - [form.pdf](../sample_data/demo/form_urgent.pdf)
* The form will have `Urgent` as document type. 

* Navigate to BigQuery and check for the extracted data inside `validation` dataset and `validation_table`.

* You could also run sample query from the Cloud Shell (to output all extracted entities from the form):
  ```shell
  ./sql-scripts/run_query.sh entities
  ```
* Sample output:

```shell
+----------------------+--------------------------------------+----------------+----------------------+--------------------+----------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------+-----------------+------------+---------------------------------------------------------------------------------+------------------------------------------------------------+
|         uid          |               case_id                | document_class | classification_score | is_hitl_classified |    document_type     |         timestamp          |                                                     gcs_doc_path                                                     | corrected_value | confidence |                                      name                                       |                           value                            |
+----------------------+--------------------------------------+----------------+----------------------+--------------------+----------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------+-----------------+------------+---------------------------------------------------------------------------------+------------------------------------------------------------+
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.94 | Are you currently taking any medication? (If yes, please describe               | Vyvanse (25mg) daily for attention.                        |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.93 | _Phone                                                                          | walker@cmail.com (906                                      |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.91 | Zip                                                                             | 07082                                                      |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |        0.9 | City                                                                            | Towaco                                                     |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.89 | State                                                                           | NJ                                                         |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.89 | DOB                                                                             | 09/04/1986                                                 |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.88 | Gender                                                                          | F                                                          |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.87 | Name                                                                            | Sally Walker                                               |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.85 | Marital Status                                                                  | Single                                                     |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.84 | Describe your medical concerns (symptoms, diagnoses, etc                        | Ranny nose, mucas in thwat, weakness, aches, chills, tired |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.83 | Date                                                                            | 9/14/19                                                    |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.82 | Address                                                                         | 24 Barney Lane                                             |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.81 | Occupation                                                                      | Software Engineer                                          |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.81 | Emergency Contact                                                               | Eva Walker                                                 |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |        0.8 | Email                                                                           | Sally, walker@cmail.com                                    |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.77 | Referred By                                                                     | None                                                       |
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   | -1                   |              false | Non-urgent           | 2024-02-22T01:01:14.314760 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf               | NULL            |       0.76 | Emergency Contact Phone                                                         | (906)334-8926                                              |
+----------------------+--------------------------------------+----------------+----------------------+--------------------+----------------------+----------------------------+----------------------------------------------------------------------------------------------------------------------+-----------------+------------+---------------------------------------------------------------------------------+------------------------------------------------------------+
```
## Human In the Loop (HITL) Demo
* Go to Claims Data Activator main page.
* Click on View for one of the Forms.
* Correct values to one of the Fields and submit **Save** button.
* See the corrected value saved to BigQuery:
  ```shell
  ./sql-scripts/run_query.sh corrected_values
  ```
* Sample output:
```shell
+----------------------+--------------------------------------+----------------+--------------------+----------------------------+--------------------------------------------------------------------------------------------------------+------------------+-----------------------+------------+--------+
|         uid          |               case_id                | document_class | is_hitl_classified |         timestamp          |                                              gcs_doc_path                                              | corrected_value  |         value         | confidence |  name  |
+----------------------+--------------------------------------+----------------+--------------------+----------------------------+--------------------------------------------------------------------------------------------------------+------------------+-----------------------+------------+--------+
| 1Tw6wm3XEBn0PMVnYv6A | d1285180-d11d-11ee-adcf-4a83c9b583c0 | generic_form   |              false | 2024-02-22T01:11:53.245232 | gs://cda-ek-test-07-document-upload/d1285180-d11d-11ee-adcf-4a83c9b583c0/1Tw6wm3XEBn0PMVnYv6A/form.pdf | walker@cmail.com | walker@cmail.com (906 |       0.93 | _Phone |
+----------------------+--------------------------------------+----------------+--------------------+----------------------------+--------------------------------------------------------------------------------------------------------+------------------+-----------------------+------------+--------+

```

* If you now re-run entities query, you will see corrected_value listed as well:
  ```shell
  ./sql-scripts/run_query.sh entities
  ```

## Connecting to the existing DocAI processors

### Granting Cross-Org permissions 
In this section, you will enable access to the trained DocAI processors available inside joonix environment (different from Argolis). 

* Modify  policy constraint inside the Argolis to allow cross org access:
  *  Go to GCP Cloud Shell of youur Argolis environment/Project and run following command to change `constraints/iam.allowedPolicyMemberDomain` constraint to `Allowed All`:
  ```shell
  export PROJECT_ID=
  gcloud services enable orgpolicy.googleapis.com
  gcloud org-policies reset constraints/iam.allowedPolicyMemberDomains --project=$PROJECT_ID
  ```

* Grant accesses for DocAI service account to the Cloud Storage for view/write access:

```shell
  export PROJECT_DOCAI_NUMBER=691579255811
  gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-docai-output --member="serviceAccount:service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com" --role="roles/storage.admin"
  gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-document-upload --member="serviceAccount:service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com" --role="roles/storage.objectViewer"
```

* Share `PROJECT_ID` with the admin user of `prior-auth-poc` Project (joonix) ([dharmeshpatel](dharmeshpatel@google.com) or [evekhm](evekhm@google.com)) so that following service account will be added to the dedicated member group (Only Org admin would be able to run command below):

Following command below to be executed by the admin user of the `prior-auth-poc` Project:
```shell
GROUP_EMAIL="cda-engine-argolis@hcls.joonix.net"
gcloud identity groups memberships add --group-email="${GROUP_EMAIL}" --member-email="gke-sa@${PROJECT_ID}.iam.gserviceaccount.com" --roles=MEMBER
```

### Modifying config.json file
* Configuration file is stored in the GCS bucket and dynamically used by the pipeline: `gs://${PROJECT_ID}-config/config.json`
  

* For the DocAI access, use the pre-configured file:  

  ```shell
  gsutil cp common/src/common/config/lab1.json "gs://${PROJECT_ID}-config/config.json"
  ```
  
### Testing New Configuration

Now you can use  DocAI Classifier and Specialized CDE trained for Prior-Auth Forms, such as [PA Texas Forms](../sample_data/bsc_demo/pa-form-1.pdf) and [BSC PA Forms](../sample_data/bsc_demo/bsc-dme-pa-form-1.pdf).

* Upload a collection of different forms from [bsc_demo](../sample_data/bsc_demo) directory and see how are they classified as `BSC Prior-Auth Form` , `Prior-Authorization Form` accordingly: 

  * You could use UI to upload forms one by one or 
  * Use a batch upload via a wrapper script.  
    * Following command will take four forms inside `bsc_demo` directory and trigger the pipeline. 
      * Generated case_ids will have a prefix as specified under -l argument (_demo01_ in this case).
      * One of the forms (`Package-combined.pdf`) is a single PDF containing four different forms merged together. 
        * The trained splitter will on the fly split the documents and use extractors for each of the corresponding document types to do data extraction
        * All forms extracted and original PDF will have the same `case_id`.
     ```shell
     ./start_pipeline.sh -d sample_data/demo -l demo01
     ```
    * Following command will upload 10 PA Texas Forms and 10 BSC forms:
   ```shell
    ./start_pipeline.sh -d sample_data/forms-10 -l test
   ```

## Data Visualization 

Sample views are available in `sql-scripts`

```shell
./sql-scripts/run_query.sh
```

Try out:
```shell
./sql-scripts/run_query.sh diagnose
```

Sample Output:
```shell
+-------+----------+-------------------------------------+
|  ZIP  | DiagCode |             Description             |
+-------+----------+-------------------------------------+
| 83258 | C46      | Kaposi sarcoma                      |
| 79450 | B17      | Other acute viral hepatitis         |
| 54684 | T91.2    | Sequelae of other fracture of thora |
| 52758 | M31      | Other necrotizing vasculopathies    |
| 35204 | R20.2    | Paraesthesia of skin                |
| 17969 | Z91.8    | Personal history of other specified |
| 70998 | M90.5    | Osteonecrosis in other diseases cla |
| 96315 | 036.2    | Maternal care for hydrops fetalis   |
| 68282 | N89.2    | Severe vaginal dysplasia, not elsew |
| 91000 | G57.5    | Tarsal tunnel syndrome              |
+-------+----------+-------------------------------------+

```
## Troubleshooting

### Ingress cannot get deployed

If you see that Ingress does not become Green in the Console UI and running command below does not resolve to the external IP address `ADDRESS`, this means ingress failed to get deployed.

```shell
kubectl get ing
```

One way to fix it is to delete ingress (along with the certificate) and re-run terraform:

Delete ingress (this operation will take ~ 5 minutes):
```shell
kubectl delete ing external-ingress
```

Wait until operation completes and run:
```shell
kubectl delete managedcertificate gclb-managed-cert
```

Now we need to apply terraform:
```shell
bash -e ./init_ingress.sh
```

### ERROR: This site can’t provide a secure  
Error: This site can’t provide a secure connection ERR_SSL_VERSION_OR_CIPHER_MISMATCH

This might be related to the Certificate still being in the `Provisioning` state.
You could check that by running following command: 

```shell
kubectl describe managedcertificate
```

Check if  Status:  `Provisioning` is still in place, 5-10 minutes might be required additionally.

When Certificate is provisioned, sample output looks like following (with `Active` status):
```shell
Name:         gclb-managed-cert
Namespace:    default
Labels:       <none>
Annotations:  <none>
API Version:  networking.gke.io/v1
Kind:         ManagedCertificate
Metadata:
  Creation Timestamp:  2023-05-04T21:04:29Z
  Generation:          3
  Resource Version:    62571
  UID:                 d327b407-ebb0-4555-86e2-d69010893674
Spec:
  Domains:
    yor_domain.com
Status:
  Certificate Name:    mcrt-7dee5265-3f52-4876-9bb3-d698a91922f3
  Certificate Status:  Active
  Domain Status:
    Domain:     YOUR-DOMAIN
    Status:     Active
  Expire Time:  2023-08-02T14:04:32.000-07:00
Events:
  Type    Reason  Age   From                            Message
  ----    ------  ----  ----                            -------
  Normal  Create  23m   managed-certificate-controller  Create SslCertificate mcrt-7dee5265-3f52-4876-9bb3-d698a91922f3
```

If you are getting `FailedNotVisible`, something went wrong when Provisioning the cert:

```text
Status:
  Certificate Name:    mcrt-1b1908e3-d7cb-4cb8-8a26-883ab57dda5f
  Certificate Status:  Provisioning
  Domain Status:
    Domain:  YOUR-DOMAIN
    Status:  FailedNotVisible
Events:
  Type    Reason  Age   From                            Message
  ----    ------  ----  ----                            -------
  Normal  Create  40m   managed-certificate-controller  Create SslCertificate mcrt-1b1908e3-d7cb-4cb8-8a26-883ab57dda5f
```

You could try fixing it by re-creating the cert:

```shell
kubectl delete managedcertificate gclb-managed-cert
```

Then re-applying terraform scripts:
```shell
bash -e ./init_ingress.sh
```

Re-view suggested changes by terraform, that will be creating of new managed certificate and re-building of two cloud run services (unfortunately Terraform does that each time).

Type `yes` to confirm changes.

Check the state of the re-created certificate:
```shell
kubectl describe managedcertificate
```

If it `Certificate Status:  Active`, issue is fixed!

### ERROR: googleapi: Error 400: Master version "1.XX.XX-gke.XXX" is unsupported.
This might be related to the deprecated version of GKE. 

To fix this error, try running './init_foundation.sh' after updating the kubernetes engine version in the following terraform file:
`terraform/stages/foundation/main.tf` - inside `module gke`

```text
kubernetes_version = "1.29.0-gke.1381000"
```
You can find the latest stable GKE version from [here.](https://cloud.google.com/kubernetes-engine/docs/release-notes-stable)
