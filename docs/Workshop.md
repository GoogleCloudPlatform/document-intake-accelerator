## About

This is a customized version of installation Guide that installs CDA engine using Public End point and connects to the existing DocAI Processor Project.
For other flavours and more detailed steps, check the original full [README](../README.md).

## Pre-requisites

### Access to Git Repo
* Request access to [Git Repo](https://github.com/hcls-solutions/claims-data-activator).

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
  [//]: # (- Enable Google auth provider, and select Project support email to your admin’s email. Leave the Project public-facing name as-is. Then click Save.)
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
This command will take **~10 minutes** to complete, and it will take another **10-15 minutes** for ingress to get ready.  
You could check status of ingress by either navigating using Cloud Shell to
[GKE Ingress](https://console.cloud.google.com/kubernetes/ingress/us-central1/main-cluster/default/external-ingress/details) and waiting till it appears as solid green.

## Out of the box UI demo test
This relies on the available out-of-the box Form parser.

* To access the Application UI, Navigate to Domain Name using the browser and login using username/password created in the previous steps.
* Upload a sample document (e.g. available in `sample_data/demo/form.pdf`)  using *Upload a Document* button.  From *Choose Program* drop-down, select `California` state.
  * Right now, the Form Processor is set up as a default processor (since no classifier is deployed or trained), so each document will be processed with the Form Parser and extracted data will be streamed to the BigQuery.
* As you click Refresh Icon on the top right, you will see different Status the Pipeline goes through: *Classifying -> Extracting -> Approved* or *Needs Review*.

* If you select *View* action, you will see the key/value pairs extracted from the Document.

* Navigate to BigQuery and check for the extracted data inside `validation` dataset and `validation_table`.


[//]: # (## Connecting Trained DocAI Processors)

[//]: # (```shell)

[//]: # (export PROJECT_ID=)

[//]: # (export DOCAI_PROJECT_ID=prior-auth-poc)

[//]: # (PROJECT_DOCAI_NUMBER=691579255811)

[//]: # (gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-docai-output --member="serviceAccount:service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com" --role="roles/storage.admin")

[//]: # (gcloud storage buckets add-iam-policy-binding  gs://${PROJECT_ID}-document-upload --member="serviceAccount:service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com" --role="roles/storage.objectViewer")

[//]: # (```)

[//]: # ()
[//]: # (Share your Project_ID:)

[//]: # (<To be run in the joonix>)

[//]: # (```shell)

[//]: # (GROUP_EMAIL="cda-engine-argolis@hcls.joonix.net")

[//]: # (gcloud identity groups memberships add --group-email="${GROUP_EMAIL}" --member-email="serviceAccount:gke-sa@${PROJECT_ID}.iam.gserviceaccount.com" --roles=MEMBER)


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