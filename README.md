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

Before starting, activate Python virtual env in your terminal:
```shell
python3 -m venv ~/venv/pa
source ~/venv/pa/bin/activate
```

### Prerequisites
*Important*: User needs to have Project **owner** role in order to deploy  terraform setup.
```
export PROJECT_ID=<GCP Project ID>
export API_DOMAIN=mydomain.com
```
Note, If you do not have a custom domain, leave a dummy one `mydomain.com` (needs to be set to a legal name as a placeholder) and then later run an optional step below to configure using Ingress IP address instead.


```shell
gcloud config set project $PROJECT_ID
```

Run following commands locally (not required for Cloud Shell):
```shell
gcloud auth login
gcloud auth application-default login
gcloud auth application-default set-quota-project $PROJECT_ID
```

### GCP Organization policy

Run the following commands to update Organization policies (Required for managed environments such as Argolis):
```
ORGANIZATION_ID=$(gcloud organizations list --format="value(name)")
gcloud resource-manager org-policies disable-enforce constraints/compute.requireOsLogin --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/compute.vmExternalIpAccess --organization=$ORGANIZATION_ID
gcloud resource-manager org-policies delete constraints/compute.requireShieldedVm --organization=$ORGANIZATION_ID
```

Or, change the following Organization policy constraints in [GCP Console](https://console.cloud.google.com/iam-admin/orgpolicies)
- constraints/compute.requireOsLogin - Enforced Off
- constraints/compute.vmExternalIpAccess - Allow All
- constraints/compute.requireShieldedVm - Enforced Off

### Setup and Run Demo

Simplified steps below makes installation faster by encapsulating details in the wrapper scripts.
For the detailed original flow see [Detailed Steps](#steps_original.md).

#### Terraform 
Run init step (will prepare for terraform execution and do terraform apply with auto-approve):
```shell
./init.sh
```

When not using custom DNS name (if you left `mydomain.com` above as API_DOMAIN, switch to using Ingress IP (shall be skipped when using custom domain name):
```shell
source ./init_domain_with_ip.sh
```

#### Deploy microservices
```shell
./deploy.sh
```

#### Trigger the pipeline
*NB: Currently only pdf documents are supported, so if you have a jpg or png, please first convert it to pdf.*

To trigger document processing and extraction of the data to further ingest in BigQuery,
 you must upload an empty file named START_PIPELINE into a batch data folder inside ${PROJECT_ID}-pa-forms GCS bucket.

See which pdf forms files are in the demo folder:
```shell
  ls sample_data/demo/*.pdf
```

Following step will upload to GS bucket documents from the sample_data/demo directory and trigger the pipeline with `mybatch-demo` tag:
```shell
./start_pipeline demo mybatch-demo
```

Alternatively, you can manually upload *pdf* forms to the **gs://${PROJECT_ID}-pa-forms/<mydir>** bucket and drop empty START_PIPELINE file to trigger the pipeline execution.
After putting START_PIPELINE, the pipeline is automatically triggered  to process  all PDF documents inside the gs://${PROJECT_ID}-pa-forms/<mydir> folder.

```shell
touch START_PIPELINE
gsutil cp START_PIPELINE gs://${PROJECT_ID}-pa-forms/<mydir>
```

This should take around two minutes for operation to complete. 
When processed, documents are moved to `gs://${PROJECT_ID}-pa-forms/processed` directory and also copied to gs://${PROJECT_ID}-document-upload with unique identifiers. 


To verify the Pipeline worked, go to BigQuery and check for the extracted data inside `validation` dataset and `validation_table`.
Or run the following Query:
```shell
./utils/run_query.sh
```

Sample output:
```shell
+----------------------------------------------+----------------------+----------------+----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
|                   case_id                         |         uid          | document_class |    document_type     |                                                                                                                                                                                                                entities                                                                                                                                                                                                                |      timestamp      |
+----------------------------------------------+----------------------+----------------+----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
| mybatch-demo_63a8295e-90a6-11ed-83f9-fd3ef939e375 | VTnRhdt4oMH6UbeMyaQb | claims_form    | supporting_documents | {"zip": "07082", "state": "NJ", "referred_by": "None", "occupation": "Software Engineer", "name": "SALLY WALKER", "medications": null, "medical_condition": null, "marital_status": "Single", "gender": "F", "emergency_contact_phone": "(906) 334-8976", "emergency_contact": "Eva Walker", "email": "Sally, waller@cmail.com", "dob": "09/04/1986", "date": "9/14/19", "city": "Towaco", "address": "24 barney lane", "PHONE": null} | 2023-01-10 05:20:49 |
+----------------------------------------------+----------------------+----------------+----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
```

## Next Steps
In the next steps you will set up specialized Processor and Classifier to handle custom Prior-Auth form. Previously only Form parser available out-of-the-box was used.

**Pre-requisite** 
There should be at least 20 (recommended 50) customer  forms with filled data (of the same type), which could be used for training the processor for extraction and classification.

### Preparations
* Create new `sample_data/custom_forms` directory
* Convert existing forms to pdf (if not in pdf format) and add them to the new `sample_data/custom_forms` directory.

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
  - For extracted data to be properly mapped to the created Labels, you need to customize schema inside (common/src/common/docai_entity_mapping.json)[common/src/common/docai_entity_mapping.json] under prior_auth_form section. 
    - This is ued to specify which entities will be extracted and name mappings.
  - Following utility would be handy to list all the entities the Trained processor Could extract from the document:

    ```shell
    export RPOCESSOR_ID=<your_processor_id>
    python utils/gen_config_processor.py -f sample_data/custom_forms/<my-sample-form>.pdf 
    ```
  - In the Python output, everything between START GENERATED CONFIGURATION and END GENERATED CONFIGURATION is to be placed inside `common/src/common/docai_entity_mapping.json` (under prior_auth_form section)  and copied to GS config directory. 

  ```shell
      "all": {
          "prior_auth_form": {
              "default_entities": {
                 <--- COPY_HERE ---> 
              }
          }
  ```
  For example: 
  ```shell
      "all": {
          "prior_auth_form": {
              "default_entities": {
                "issurerName": ["issurerName"],
                "routineFax": ["routineFax"],
                "modificationFax": ["modificationFax"],
              }
          }
  ```

Upload config document to GS bucket:  
```shell
 gsutil cp ../../../common/src/common/docai_entity_mapping.json gs://$PROJECT_ID/config/docai_entity_mapping.json
```

When adding new type (for examples, you already customized prior_auth_form and want to create a second Customized Processor for another form type, then following step needs to be done:)
  - Add new type of the `SUPPORTING_DOCS`  inside (common/src/common/config.py)[common/src/common/config.py]: 

  For example: 
```python
SUPPORTING_DOCS = ["claims_form", "prior_auth_form", "my_new_form"]
  ```

### Custom Document Classifier
Classifier allows to map form to the processor required for data extraction. 

>> If you have just one sample_form.pdf, and you want to use it for classifier, use following utility to copy same form into the gcs bucket, later to use for classification. At least 10 instances are needed (all for Training set).
```shell
utils/copy_forms.sh -f sample_data/<path_to_form>.pdf -d gs://<path_to_gs_uri> -c 10
```

Configure Custom Document Classifier (Currently feature is not available for GA and needs to be requested via the [form](https://docs.google.com/forms/d/e/1FAIpQLSfDuC9bGyEwnseEYIC3I2LvNjzz-XZ2n1RS4X5pnIk2eSbk3A/viewform))
  - Create New Labels for all currently active form types: `prior_auth_form` and`claims_form`.
  - Train Classifier to using sample forms to classify the labels.
  - Deploy the new trained version via the UI.
  - Set the new version as default and test it manually via the UI by uploading the test document. is it classified properly?

### Custom Configuration
  - Use Classifier ID to setup [common/src/common/parser_config.json](common/src/common/parser_config.json)

  - Config is stored in the bucket: `gs://${PROJECT_ID}/config/parser_config.json`
    - Download config locally or when using Cloud Shell, use cloud shell editor to do changes to `gs://${PROJECT_ID}/config/parser_config.json` file

      ```shell
      gsutil cp "gs://${PROJECT_ID}/config/parser_config.json" common/src/common/parser_config.json 
      ```

  - Add id of the classifier you have created (replace:
  ```shell
      "classifier": {
          "labels": {
              "goog-packaged-solution": "prior-authorization"
          },
          "location": "us",
          "parser_type": "CUSTOM_CLASSIFICATION_PROCESSOR",
          "processor_id": "projects/<project_id>/locations/us/processors/<classifier-id>"
      }
  ```

Upload config:
```shell
gsutil cp common/src/common/parser_config.json "gs://${PROJECT_ID}/config/parser_config.json"
````

### Rebuild / RE-deploy
- Rebuild/re-dploy applications using skaffold
  ```shell
  source SET
  gcloud container clusters get-credentials main-cluster --region $REGION --project $PROJECT_ID
  skaffold run  -p dev --default-repo=gcr.io/${PROJECT_ID}
  ```
### Trigger pipeline
*NB: Currently only pdf documents are supported, so if you have a jpg or png, please first convert it to pdf.*
- Upload test forms to the `gs://${PROJECT_ID}-pa-forms/<name-of-form_type>`

For example:
```shell
gsutil -m cp -r sample_data/bsc_pa/* gs://${PROJECT_ID}-pa-forms/bsc_pa/
```

- Trigger processing of a folder the forms:
  ```shell
    ./start_pipeline.sh <name-of-form_type>
  ```


For example:
```shell
 ./start_pipeline.sh bsc_pa
```

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

### Eventarc error on init
- Is due to timing and re-running `terraform apply -target=module.eventarc`  fixes the issue.


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
