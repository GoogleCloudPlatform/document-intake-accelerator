# Document Intake Accelerator

> A pre-packaged and customizable solution to accelerate the development of end-to-end document processing workflow incorporating Document AI parsers and other GCP products (Firestore, BigQuery, GKE, etc). The goal is to accelerate the development efforts in document workflow with many ready-to-use components.

## Key features
- End-to-end workflow management: document classification, extraction, validation, profile matching and Human-in-the-loop review.
- API endpoints for integration with other systems.
- Customizable components in microservice structure.
- Solution architecture with best practices on Google Cloud Platform.

## Getting Started to Deploy the DocAI Workflow

Following steps could be run either from the CLoud Shell of the Project or locally,

When running locally, following tools need to be installed in advance:
* skaffold (tested with v2.0.2)
* gcloud
* kubectl
* terraform (tested with Terraform v1.3.5)
* python

Also make sure to update to the latest gcloud tool:
```
# Tested with gcloud v400.0.0
gcloud components update
```

And before starting, activate Python virtual env in your terminal:
```shell
python3 -m venv ~/venv/pa
source ~/venv/pa/bin/activate
```

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
kubectl describe ingress | grep Address
```
- This will print the Ingress IP like below:
  ```
  Address: 123.123.123.123
  ```

**NOTE**: If you don’t have a custom domain, and want to use the Ingress IP address as the API endpoint:
- Change the TF_VAR_api_domain to this Ingress endpoint, and re-deploy CloudRun.
  ```
  export TF_VAR_api_domain=$(kubectl describe ingress | grep Address | awk '{print $2}')
  terraform apply -target=module.cloudrun
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
