# Table of contents

- [About](#about)
- [Pre-requisites](#pre-requisites)
  - [Access to Git Repo](#access-to-git-repo)
  - [Create new Project in Argolis](#create-new-project-in-argolis)
- [Installation](#installation)
  - [Setting up](#setting-up)
  - [Terraform](#terraform)
  - [Front End Config](#front-end-config)
  - [Enable Firebase Auth](#enable-firebase-auth)
  - [Deploy microservices](#deploy-microservices)
- [Out of the box UI demo flow](#out-of-the-box-ui-demo-flow)
- [Connecting to the existing DocAI processors](#connecting-to-the-existing-docai-processors)
  - [Granting Cross-Org permissions](#granting-cross-org-permissions)
  - [Modifying config.json file](#modifying-configjson-file)
  - [Testing New Configuration](#testing-new-configuration)
- [Troubleshooting](#troubleshooting)
  - [ERROR: This site can’t provide a secure](#error-this-site-cant-provide-a-secure)
## About

This is a customized version of installation Guide that installs CDA engine using Public End point and connects to the existing DocAI Processor Project.
For other flavours and more detailed steps, check the original full [README](../README.md).

## Pre-requisites

### Access to Git Repo
* Request access to [this](https://github.com/hcls-solutions/claims-data-activator) Git Repo by reaching out to [dharmeshpatel](dharmeshpatel@google.com) or [evekhm](evekhm@google.com).

### Create New Project in Argolis
* You will need access to Argolis environment and project owner rights.
* Installation will happen in the newly created Argolis project.

## Installation
### Setting up

* Get the Git Repo in the Cloud Shell:
```shell
git clone git@github.com:hcls-solutions/claims-data-activator.git
cd claims-data-activator
```

* Set env variable for _PROJECT_ID_:
```shell
export PROJECT_ID=<YOUR_PROJECT_ID>
``` 

* Reserve External IP:
```shell
gcloud config set project $PROJECT_ID
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
```shell
gcloud services enable dns.googleapis.com
gcloud services enable domains.googleapis.com
```

* Register a Cloud Domain:
  * If you want to use Argolis DNS (<ldap>.demo.altostrat.com), follow the guide [go/argolis-dns](go/argolis-dns). 
    * Navigate to [Cloud DNS](https://console.cloud.google.com/net-services/dns/zones) and create ZONE as described in the guide for <ldap>.demo.altostrat.com
    * Request DNS managed zone (as described in [go/argolis-dns](go/argolis-dns))
  * Otherwise, purchase a [Cloud Domain](https://cloud.google.com/domains/docs/overview) 
    * Navigate to [Cloud Domain](https://console.cloud.google.com/net-services/domains/registrations), pick desired name and fill in the forms:


* Create a DNS record set of `type A` and point to the reserved external IP:
    - On the Zone details page, click on zone name (will be created by the previous step, after registering Cloud Domain).
    - Add record set.
    - Select A from the Resource Record Type menu.
    - For IPv4 Address, enter the external IP address that has been reserved.


* Set env variable for _API_DOMAIN_ registered:
```shell
export API_DOMAIN=<YOUR_DOMAIN>
````

* Verify that your domain name resolves to the reserved IP address:

```bash
  $ nslookup -query=a $API_DOMAIN
  ...(output omitted)..
``` 

### Terraform

Copy terraform sample variable file as `terraform.tfvars`:
 ```shell
cp terraform/environments/dev/terraform.sample.tfvars terraform/environments/dev/terraform.tfvars
vi terraform/environments/dev/terraform.tfvars
```

Verify `cda_external_ip` points to the reserved External IP name inside `terraform/environments/dev/terraform.tfvars`:
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
> Uncomment Line 55 in `terraform/environments/dev/providers.tf` file:
> ```shell
>  load_config_file  = false  # Uncomment this line if you do not have .kube/config file
> ```

* Run **init** step to provision required resources in GCP (will run terraform apply with auto-approve):
```shell
bash -e ./init.sh
```
This command will take **~15 minutes** to complete.
After successfully execution, you should see line like this at the end:

```shell
<...> Completed! Saved Log into /<...>/init.log
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
- In the codebase, open up microservices/adp_ui/.env in an Editor (e.g. `vi`), and change the following values accordingly.
  - REACT_APP_FIREBASE_API_KEY=`"Web API Key copied above"`

### Deploy microservices
Build/deploy microservices (using skaffold + kustomize):
```shell
./deploy.sh
```
This command will take **~10 minutes** to complete, and it will take another **10-15 minutes** for ingress to get ready and for the cert to be provisioned.  

You could check status of ingress by either navigating using Cloud Shell to
[GKE Ingress](https://console.cloud.google.com/kubernetes/ingress/us-central1/main-cluster/default/external-ingress/details) and waiting till it appears as solid green.

When ingress is Green and ready, make sure the cert is in the `Active` status. If it shows as `Provisioning`, give it another 5-10 minutes and re-check:
```shell
kubectl describe managedcertificate
```

## Out of the box UI demo flow
This relies on the available out-of-the box Form parser.

* To access the Application UI, Navigate to Domain Name using the browser and login using username/password created in the previous steps.
* Upload a sample document (e.g. [form.pdf](../sample_data/demo/form.pdf))  using *Upload a Document* button.  From *Choose Program* drop-down, select `California` state.
  * Right now, the Form Processor is set up as a default processor (since no classifier is deployed or trained), so each document will be processed with the **Form Parser** and extracted data will be streamed to the BigQuery.
* As you click Refresh Icon on the top right, you will see different Status the Pipeline goes through: *Classifying -> Extracting -> Approved* or *Needs Review*.

* If you select *View* action, you will see the key/value pairs extracted from the Document. 

* Click on the Field text box (on the Right under the Extraction Score Column) and a Bounding Box will appear on the Form, showing Location of the Label and extracted value.

* Navigate to BigQuery and check for the extracted data inside `validation` dataset and `validation_table`.

* You could also run sample query from the Cloud Shell (to output all extracted entities from the form):
  ```shell
  ./sql-scripts/run_query.sh entities
  ```
* Sample output:

```shell
+----------------------+--------------------------------------+----------------+----------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------+-----------------+------------+-----------------------------------------+
|         uid          |               case_id                | document_class |    document_type     |         timestamp          |                                                      gcs_doc_path                               | corrected_value | confidence |          name            |                   value             |
+----------------------+--------------------------------------+----------------+----------------------+----------------------------+------------------------------------------------------------------------------------------------------------------------+-----------------+------------+-----------------------------------------+
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | Phone                    | (906) 917-3486                      |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | Emergency Contact        | Eva Walker                          |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | Marital Status           | Single                              |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | Gender                   | F                                   |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | Occupation               | Software Engineer                   |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | Referred By              | None                                |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | Date                     | 9/14/19                             |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | DOB                      | 09/04/1986                          |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | Address                  | 24 Barney Lane                      |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | City                     | Towaco                              |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | Name                     | Sally Walker                        |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | State                    | NJ                                  |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | Email                    | Sally, waller@cmail.com             |
| Q1VDOuRJjE23uw3jjW3s | 0e20a0b6-eac3-11ed-81ff-6692b75136d6 | generic_form   | supporting_documents | 2023-05-04T21:32:28.441699 | gs://xxx-document-upload/0e20a0b6-eac3-11ed-81ff-6692b75136d6/Q1VDOuRJjE23uw3jjW3s/form.pdf     | NULL            |          1 | Zip                      | 07082                               |
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
+----------------------+--------------------------------------+-----------------+----------------------------+----------------------------------------------------------------------------------------------------------------+--------------------+---------------+------------+--------+
|         uid          |               case_id                | document_class  |         timestamp          |                                                  gcs_doc_path                                    |  corrected_value   |     value     | confidence |  name  |
+----------------------+--------------------------------------+-----------------+----------------------------+----------------------------------------------------------------------------------------------------------------+--------------------+---------------+------------+--------+
| Ap9QCwi3ybWjyvJimkLj | 92cc814e-eae7-11ed-a207-3ebe327e02d3 | prior_auth_form | 2023-05-05T02:27:43.236385 | gs://xxx-document-upload/92cc814e-eae7-11ed-a207-3ebe327e02d3/Ap9QCwi3ybWjyvJimkLj/pa-form-9.pdf | Inda Laec, PA Test | Inda Laec, PA |          1 | rpName |
+----------------------+--------------------------------------+-----------------+----------------------------+----------------------------------------------------------------------------------------------------------------+--------------------+---------------+------------+--------+
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
    evekhm.demo.altostrat.com
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
