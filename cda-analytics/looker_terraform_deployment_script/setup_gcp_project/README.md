# Setup GCP Project

### Prerequistes
* Existing GCP Project
* Enable APIs using below gcloud commands:
  ```
  $ gcloud config set project <project-id>

  $ gcloud services enable \
  bigquery.googleapis.com \
  bigquerystorage.googleapis.com \
  cloudresourcemanager.googleapis.com \
  compute.googleapis.com \
  cloudbuild.googleapis.com \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  domains.googleapis.com \
  dns.googleapis.com \
  file.googleapis.com \
  iap.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  monitoring.googleapis.com \
  oslogin.googleapis.com \
  pubsub.googleapis.com \
  servicenetworking.googleapis.com \
  sql-component.googleapis.com

  $ gcloud services enable \
  sqladmin.googleapis.com \
  storage-api.googleapis.com \
  secretmanager.googleapis.com \
  redis.googleapis.com \
  cloudkms.googleapis.com \
  serviceusage.googleapis.com
  ```
* A functional web domain in order to properly use Looker. Use an already existing domain or register one using [Cloud Domains](https://cloud.google.com/domains/docs/buy-register-domain)
* You will also need to have accepted the [Looker EULA](https://download.looker.com/validate). Take note of the email address you use - you’ll need to use the same one later. After accepting the EULA you don’t need to download the JARs from the webpage. We’ll do that later via the API. If you get directed straight to the download page after authenticating then you’re good to go.
  
### Terraform
* This step creates secret manager keys, service account to be used in later steps, artifact registry and cloud dns
* Navigate to looker_deployment/setup_gcp_project/terraform folder
* Update values in terraform.tfvars as per your configuration for below variables. For dns_domain do not forget the dot at the end. For example: “abc.com.”
  ```
  project_id="<project-id>"
  project_number="<project-number>"
  location="<location>"
  email_address="<your-email-address>"
  dns_domain="<domain-name>."
  ```
* Run below commands to apply terraform configurations
  ```
  $ terraform init
  $ terraform plan
  $ terraform apply
  ```
* Take note of output provided by terraform

### Authenticate to Artifact Registry
* Location is that you used in terraform.tfvars above
  ```
  $ gcloud auth configure-docker <your location>-docker.pkg.dev
  $ docker login <your location>-docker.pkg.dev
  ```

### Set Secrets
* We have created 3 secrets with empty value. Now we will add values to these secrets
* In the commands below, don’t forget to add space at the beginning of command. In your terminal, if you begin a command with a space it won’t be logged to history
* Looker license key
  ```
  $  printf "<your looker license key>" | gcloud secrets versions add looker_license_key --data-file=-
  ```
* Database password : this is required for looker internal database. Use letters and numbers only
  ```
  $  printf "<a valid database password>" | gcloud secrets versions add looker_db_pw --data-file=-
  ```
* GCM key
  ```
  $  openssl rand -base64 32 | gcloud secrets versions add gcm_key --data-file=-
  ```

### Set Domain Name Servers
* Set your domain to use Cloud DNS’s name servers outputted by terraform
* In Google Cloud  Domains you can accomplish this by selecting “Edit DNS Details", then  selecting “Custom Name Servers” and then entering the 4 nameservers that appeared in the output from executing the Terraform module