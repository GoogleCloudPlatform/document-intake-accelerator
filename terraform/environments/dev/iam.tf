locals {
  compute_engine_sa = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
  cloud_services_sa = "serviceAccount:${data.google_project.project.number}@cloudservices.gserviceaccount.com"
}

data "google_project" "project" {}

module "cloudbuild_sa_iam_bindings" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "7.4.1"

  projects = [var.project_id]
  mode     = "additive"

  bindings = {
    "roles/run.admin" = [local.compute_engine_sa, local.cloud_services_sa]
    "roles/iam.serviceAccountUser" = [local.compute_engine_sa, local.cloud_services_sa]
    "roles/compute.admin" = [local.compute_engine_sa, local.cloud_services_sa]
  }
}
