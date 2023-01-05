/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

#Creating a cloud run service

resource "google_storage_bucket" "log-bucket" {
  name                        = "${var.project_id}-${var.name}-log"
  location                    = var.region
  storage_class               = "NEARLINE"
  uniform_bucket_level_access = true
  force_destroy               = true
  labels = {
    goog-packaged-solution = "prior-authorization"
  }
}

# Creating a custom service account for cloud run
module "cloud-run-service-account" {
  source       = "github.com/terraform-google-modules/cloud-foundation-fabric/modules/iam-service-account/"
  project_id   = var.project_id
  name         = "cloudrun-${var.name}-sa"
  display_name = "This is service account for cloud run ${var.name}"

  iam = {
    "roles/iam.serviceAccountUser" = []
  }

  iam_project_roles = {
    (var.project_id) = [
      "roles/eventarc.eventReceiver",
      "roles/pubsub.publisher",
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
  output_path = ".terraform/common.zip"
}
resource "null_resource" "build-common-image" {
  triggers = {
    src_hash = data.archive_file.common-zip.output_sha
  }

  provisioner "local-exec" {
    working_dir = "../../../common"
    command = join(" ", [
      "gcloud builds submit",
      "--config=cloudbuild.yaml",
      "--gcs-log-dir=gs://${var.project_id}-${var.name}-log",
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
  source_dir  = "../../../cloudrun/${var.name}"
  output_path = ".terraform/cloudrun-${var.name}.zip"
}

resource "null_resource" "build-cloudrun-image" {
  depends_on = [
    null_resource.build-common-image,
  ]

  triggers = {
    src_hash = "${data.archive_file.cloudrun-queue-zip.output_sha}"
  }

  provisioner "local-exec" {
    working_dir = "../../../cloudrun/${var.name}"
    command = join(" ", [
      "gcloud builds submit",
      "--config=cloudbuild.yaml",
      "--gcs-log-dir=gs://${var.project_id}-${var.name}-log",
      join("", [
        "--substitutions=",
        "_PROJECT_ID='${var.project_id}',",
        "_IMAGE='${var.name}-image'",
      ])
    ])
  }
}

resource "google_cloud_run_service" "cloudrun-service" {
  # Run the following to Re-deploy this CloudRun service.
  # terraform apply -replace=module.cloudrun.google_cloud_run_service.cloudrun-service -auto-approve

  depends_on = [
    # module.cloud-run-service-account,
    null_resource.build-common-image,
    null_resource.build-cloudrun-image,
  ]

  name     = "${var.name}-cloudrun"
  location = var.region

  template {
    metadata {
      labels = {
        goog-packaged-solution = "prior-authorization"
      }
    }
    spec {
      containers {
        image = "gcr.io/${var.project_id}/${var.name}-image:latest" #Image to connect pubsub to cloud run to processtask API and fetch data from firestore
        ports {
          container_port = 8000
        }
        env {
          name  = "MAX_UPLOADED_DOCS" #thresold value for comparison with the number of uploaded docs in firesotre collection
          value = "1000"
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
