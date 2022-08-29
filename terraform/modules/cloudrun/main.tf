#Creating a cloud run service

resource "google_storage_bucket" "queue-log-bucket" {
  name                        = "${var.project_id}-queue-log"
  location                    = var.region
  storage_class               = "NEARLINE"
  uniform_bucket_level_access = true
  force_destroy               = true
}

# Creating a custom service account for cloud run
module "cloud-run-service-account" {
  source       = "github.com/terraform-google-modules/cloud-foundation-fabric/modules/iam-service-account/"
  project_id   = var.project_id
  name         = "cloudrun-sa"
  display_name = "This is service account for cloud run"

  iam = {
    "roles/iam.serviceAccountUser" = []
  }

  iam_project_roles = {
    (var.project_id) = [
      "roles/eventarc.eventReceiver",
      "roles/firebase.admin",
      "roles/firestore.serviceAgent",
      "roles/iam.serviceAccountUser",
      "roles/iam.serviceAccountTokenCreator",
      "roles/run.invoker",
      "roles/pubsub.serviceAgent",
    ]
  }
}

# Build Cloudrun image
data "archive_file" "common-zip" {
  type        = "zip"
  source_dir  = "../../../common"
  output_path = "common.zip"
}
resource "null_resource" "build-common-image" {
  triggers = {
    src_hash = "${data.archive_file.common-zip.output_sha}"
  }

  provisioner "local-exec" {
    working_dir = "../../../common"
    command = join(" ", [
      "gcloud builds submit",
      "--config=cloudbuild.yaml",
      "--gcs-log-dir=gs://${var.project_id}-queue-log",
      join("", [
        "--substitutions=",
        "_PROJECT_ID='${var.project_id}',",
        "_IMAGE='common'",
      ])
    ])
  }
}

# Build Cloudrun image
data "archive_file" "cloudrun-queue-zip" {
  type        = "zip"
  source_dir  = "../../../cloudrun/queue"
  output_path = "cloudrun-queue.zip"
}
resource "null_resource" "build-cloudrun-image" {
  depends_on = [
    null_resource.build-common-image,
  ]

  triggers = {
    src_hash = "${data.archive_file.cloudrun-queue-zip.output_sha}"
  }

  provisioner "local-exec" {
    working_dir = "../../../cloudrun/queue"
    command = join(" ", [
      "gcloud builds submit",
      "--config=cloudbuild.yaml",
      "--gcs-log-dir=gs://${var.project_id}-queue-log",
      join("", [
        "--substitutions=",
        "_PROJECT_ID='${var.project_id}',",
        "_IMAGE='queue-image'",
      ])
    ])
  }
}

resource "google_cloud_run_service" "cloudrun-service" {
  # Run the following to Re-deploy this CloudRun service.
  # terraform apply -replace=module.cloudrun.google_cloud_run_service.cloudrun-service

  depends_on = [
    # module.cloud-run-service-account,
    null_resource.build-common-image,
    null_resource.build-cloudrun-image,
  ]

  name     = var.name
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/queue-image:latest" #Image to connect pubsub to cloud run to processtask API and fetch data from firestore
        ports {
          container_port = 8000
        }
        env {
          name  = "t" #thresold value for comparison with the number of uploaded docs in firesotre collection
          value = "10"
        }
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        env {
          # API endpoint domain
          name  = "API_DOMAIN"
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
