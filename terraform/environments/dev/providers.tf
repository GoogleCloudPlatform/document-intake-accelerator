terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~>4.0"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.14.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.3.0"
    }
  }
}

provider "google" {
  project = var.project_id
}

data "google_client_config" "access_token" {}

provider "kubernetes" {
  host                   = google_container_cluster.main-cluster.endpoint
  token                  = data.google_client_config.access_token.access_token
  client_certificate     = base64decode(google_container_cluster.main-cluster.master_auth.0.client_certificate)
  client_key             = base64decode(google_container_cluster.main-cluster.master_auth.0.client_key)
  cluster_ca_certificate = base64decode(google_container_cluster.main-cluster.master_auth.0.cluster_ca_certificate)
}

provider "kubectl" {
  load_config_file = false
  host             = google_container_cluster.main-cluster.endpoint
  token            = data.google_client_config.access_token.access_token
  cluster_ca_certificate = base64decode(
    google_container_cluster.main-cluster.master_auth[0].cluster_ca_certificate,
  )
}

provider "helm" {
  kubernetes {
    host  = google_container_cluster.main-cluster.endpoint
    token = data.google_client_config.access_token.access_token
    cluster_ca_certificate = base64decode(
      google_container_cluster.main-cluster.master_auth[0].cluster_ca_certificate,
    )
  }
}
