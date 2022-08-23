locals {
  compute_engine_sa = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
  cloud_services_sa = "serviceAccount:${data.google_project.project.number}@cloudservices.gserviceaccount.com"
}

module "cloudbuild_sa_iam_bindings" {
  source  = "terraform-google-modules/iam/google//modules/projects_iam"
  version = "7.4.1"

  projects = [var.project_id]
  mode     = "additive"

  bindings = {
    "roles/run.admin" = [local.compute_engine_sa, local.cloud_services_sa]
    "roles/iam.serviceAccountUser" = [local.compute_engine_sa, local.cloud_services_sa]
    "roles/compute.admin" = [local.compute_engine_sa, local.cloud_services_sa]
    "roles/containerregistry.ServiceAgent" = [local.compute_engine_sa, local.cloud_services_sa]
    "roles/container.admin" = [local.compute_engine_sa, local.cloud_services_sa]
  }
}

# Creating a custom service account for pubsub
module "pubsub-service-account" {
    source     = "github.com/terraform-google-modules/cloud-foundation-fabric/modules/iam-service-account/"
    project_id = var.project_id
    name       = "${var.project_id}-sapub"
    display_name = "This is service account for pubsub"

    iam = {
        "roles/iam.serviceAccountUser" = []
    }

    iam_project_roles = {
        (var.project_id) = [
            "roles/run.invoker"
        ]
    }
}

# Creating a custom service account for cloud run

module "cloud-run-service-account" {
    source     = "github.com/terraform-google-modules/cloud-foundation-fabric/modules/iam-service-account/"
    project_id = var.project_id
    name       = "run-${var.project_id}-sar"
    display_name = "This is service account for cloud run"

    iam = {
        "roles/iam.serviceAccountUser" = []
    }

    iam_project_roles = {
        (var.project_id) = [
            "roles/run.invoker",
            "roles/eventarc.eventReceiver",
            "roles/firebase.admin",
            "roles/firestore.serviceAgent"
        ]
    }
}