# Deploy Looker

### Update terraform.tfvars
* Navigate to looker_deployment/deploy_looker/terraform
* Update values for below variables in terrform.tfvars. There are other variables that can be changed as per requirement but below are mandatory variables that need to be changed
  ```
  project_id            = "<project-id>"
  region                = "<location>"
  zone                  = "<zone>"
  terraform_sa_email    = "hde-accelerator-looker@<project-id>.iam.gserviceaccount.com"
  dns_managed_zone_name = "<dns-managed-zone>"
  gke_node_zones        = ["<zone>"]
  looker_k8s_repository = "<location>-docker.pkg.dev/<project-id>/looker/looker"
  looker_helm_repository = "oci://<location>-docker.pkg.dev/<project-id>/looker/looker-helm"
  envs = {
    dev = {
        db_secret_name                = "looker_db_pw"
        gcm_key_secret_name           = "gcm_key"
        looker_node_count             = 1
        looker_version                = "22.18"
        looker_k8s_issuer_admin_email = "<your-email>"
        }
    }
  ```

### Terraform
* This step creates vpc, subnet, private service access, cloud router, cloud sql, filestore, memorystore, GKE cluster
* Configuration deploys looker image created and Helm chart created in previous steps
* Execute below commands
  ```
  $ terraform init
  $ terraform plan
  $ terraform apply
  ```

### Access Looker
* Open link \<env\>.looker.\<domain\> to access looker
  * env : this is env defined in terraform.tfvars above
  * domain : this is your domain name
  
### Setup Initial Looker Account
* Select “Already have a license” and then fill in the required info - you’ll need to use your Looker license key
