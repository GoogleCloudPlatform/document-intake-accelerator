# Original Deployment Steps

### Prerequisites
*Important*: User needs to have Project **owner** role in order to deploy the terraform setup.
```
export PROJECT_ID=<GCP Project ID>
export REGION=us-central1
export ADMIN_EMAIL=<Your Email>
export BASE_DIR=$(pwd)

# A custom domain like your-domain.com. If you do not have one, use temporally a legal name as a placeholder, do not leave it blank,
and later follow steps as described below for using the Ingress IP address instead.
export API_DOMAIN=<Your Domain>
```

```shell
gcloud config set project $PROJECT_ID
```

Run following commands locally (not required for Cloud Shell)
```shell
gcloud auth application-default login
gcloud auth application-default set-quota-project $PROJECT_ID
```

### GCP Organization policy

Run the following commands to update Organization policies:
```
export ORGANIZATION_ID=<your organization ID>
gcloud resource-manager org-policies disable-enforce constraints/compute.requireOsLogin --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/compute.vmExternalIpAccess --organization=$ORGANIZATION_ID
```

Or, change the following Organization policy constraints in [GCP Console](https://console.cloud.google.com/iam-admin/orgpolicies)
- constraints/compute.requireOsLogin - Enforced Off
- constraints/compute.vmExternalIpAccess - Allow All

### GCP foundation - Terraform

Set up Terraform environment variables and GCS bucket for state file:

```
export TF_VAR_api_domain=$API_DOMAIN
export TF_VAR_admin_email=$ADMIN_EMAIL
export TF_VAR_project_id=$PROJECT_ID
export TF_BUCKET_NAME="${PROJECT_ID}-tfstate"
export TF_BUCKET_LOCATION="us"

# Create Terraform Statefile in GCS bucket.
bash setup/setup_terraform.sh
```

Run Terraform

```
cd terraform/environments/dev
terraform init -backend-config=bucket=$TF_BUCKET_NAME

# enabling GCP services first.
terraform apply -target=module.project_services -target=module.service_accounts -auto-approve

# Run the rest of Terraform
terraform apply

# ...
# Enter yes at the promopt to apply Terraform changes.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes
```

**IMPORTANT**: Run the script to update config JSON based on terraform output.
```
# in terraform/environments/dev folder
bash ../../../setup/update_config.sh
```

Connect to the `default-cluster`:
```
gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID
```


Get the API endpoint IP address, this will be used in Firebase Auth later.
```
kubectl describe ingress default-ingress | grep Address

```
- This will print the Ingress IP like below:
  ```
  Address: 123.123.123.123
  ```

**NOTE**: If you don’t have a custom domain, and want to use the Ingress IP address as the API endpoint:
- Change the TF_VAR_api_domain to this Ingress endpoint, and re-deploy CloudRun.
  ```
  export TF_VAR_api_domain=$(kubectl describe ingress default-ingress | grep Address | awk '{print $2}')
  terraform apply -target=module.cloudrun-queue -target=module.cloudrun-start-pipeline
  ```

### Enable Firebase Auth

- Before enabling firebase, make sure [Firebase Management API](https://console.cloud.google.com/apis/api/firebase.googleapis.com/metrics) should be disabled in GCP API & Services.
- Go to Firebase Console UI to add your existing project. Select “Pay as you go” and Confirm plan.
- On the left panel of Firebase Console UI, go to Build > Authentication, and click Get Started.
- Select Google in the Additional providers
- Enable Google auth provider, and select Project support email to your admin’s email. Leave the Project public-facing name as-is. Then click Save.
- Go to Settings > Authorized domain, add the following to the Authorized domains:
  - Web App Domain (e.g. adp-dev.cloudpssolutions.com)
  - API endpoint IP address (from kubectl describe ingress | grep Address)
  - localhost
- Go to Project Overview > Project settings, you will use this info in the next step.
- In the codebase, open up microservices/adp_ui/.env in an Editor (e.g. VSCode), and change the following values accordingly.
  - REACT_APP_BASE_URL
    - The custom Web App Domain that you added in the previous step.
    - Alternatively, you can use the API Domain IP Address (Ingress), e.g. http://123.123.123.123
  - REACT_APP_API_KEY - Web API Key
  - REACT_APP_FIREBASE_AUTH_DOMAIN - $PROJECT_ID.firebaseapp.com
  - REACT_APP_STORAGE_BUCKET - $PROJECT_ID.appspot.com
  - REACT_APP_MESSAGING_SENDER_ID
    - You can find this ID in the Project settings > Cloud Messaging
  - (Optional) REACT_APP_MESSAGING_SENDER_ID - Google Analytics ID, only available when you enabled the GA with Firebase.

### Deploying Kubernetes Microservices

Build all microservices (including web app) and deploy to the cluster:
```
cd $BASE_DIR
skaffold run -p prod --default-repo=gcr.io/$PROJECT_ID
```

### Update DNS with custom Domain (Optional)

Get the Ingress external IP:
```
kubectl describe ingress | grep Address
```

Add an A Record in your DNS setting to point to the Ingress IP Address, e.g. in https://domains.google.com/.
- Once added, it may take 5-10 mins to populate to the DNS network.