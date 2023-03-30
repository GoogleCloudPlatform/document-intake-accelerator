# Set Permissions for Flattened Views

### Update terraform.tfvars
* Navigate to looker_deployment/set_permissions/terraform
  ```
  project_id  =   "<project-id>"
  ```

### Terraform
* This terraform configuration creates a service account to allow access to  flattened views. Configuration also creates looker_scratch dataset for creating PDT
  ```
  $ terraform init
  $ terraform plan
  $ terraform apply
  ```
* Make sure authorized views are created on base dataset to access custom_fhir_flattened_views
* use service account: **hde-accelerator-bq-sa@\<project-id\>.iam.gserviceaccount.com**
