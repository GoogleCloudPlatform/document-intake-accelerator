project_id            = "<project-id>"
region                = "<location>"
zone                  = "<zone>"
terraform_sa_email    = "hde-accelerator-looker@<project-id>.iam.gserviceaccount.com"
prefix                = "test"
dns_managed_zone_name = "<dns-managed-zone>"
db_tier               = "db-custom-2-7680"
gke_node_zones        = ["<zone>"]
gke_node_tier         = "e2-standard-16"
gke_node_count_min    = 3
gke_node_count_max    = 5
looker_k8s_repository = "<location>-docker.pkg.dev/<project-id>/looker/looker"
looker_helm_repository = "oci://<location>-docker.pkg.dev/<project-id>/looker/looker-helm"
envs = {
  dev = {
    db_secret_name                = "looker_db_pw"
    gcm_key_secret_name           = "gcm_key"
    looker_node_count             = 2
    looker_version                = "22.18"
    looker_k8s_issuer_admin_email = "<your-email>"
  }
}