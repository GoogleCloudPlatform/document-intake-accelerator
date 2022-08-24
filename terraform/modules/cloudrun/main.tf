#Creating a cloud run service

resource "google_storage_bucket" "queue-log-bucket" {
  name          = "${var.project_id}-queue-log"
  location      = var.region
  storage_class = "NEARLINE"
  uniform_bucket_level_access = true
}

# Build Cloudrun image
resource "null_resource" "provision" {
  provisioner "local-exec" {
    command = "gcloud builds submit -t gcr.io/${var.project_id}/queue-image ../../../cloud_run/Queue --gcs-log-dir=gs://${var.project_id}-queue-log"
  }
}

# Creating a custom service account for cloud run

module "cloud-run-service-account" {
    source     = "github.com/terraform-google-modules/cloud-foundation-fabric/modules/iam-service-account/"
    project_id = var.project_id
    name       = "cloudrun-sa"
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

resource "google_cloud_run_service" "cloudrun-service" {
  depends_on = [
    module.cloud-run-service-account,
    null_resource.provision
  ]
  # count = "${var.cloudrun_deploy ? 1 : 0}"
  name     = var.name
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/queue-image:latest"  #Image to connect pubsub to cloud run to processtask API and fetch data from firestore
        ports{
            container_port=8000
        }
        env {
          name = "t"  #thresold value for comparison with the number of uploaded docs in firesotre collection
          value = "10"
        }
        env {
          name = "PROJECT_ID"
          value = var.project_id
        }
        env {
          # API endpoint domain
          name = "API_DOMAIN"
          value = var.api_domain
        }
      }
      service_account_name = module.cloud-run-service-account.email
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
    }
}

