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

locals {
  default_sa_list = [
    "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com",
    "serviceAccount:${data.google_project.project.number}@cloudservices.gserviceaccount.com",
    "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com",
    "serviceAccount:service-${data.google_project.project.number}@gcp-sa-aiplatform.iam.gserviceaccount.com",
  ]
}

data "google_project" "project" {}

module "service_accounts" {
  source       = "terraform-google-modules/service-accounts/google"
  version      = "4.2.2"
  project_id   = var.project_id
  names        = ["deployment-${var.env}"]
  display_name = "deployment-${var.env}"
  description  = "Deployment SA for ${var.env}"
  project_roles = [for i in [
    "roles/aiplatform.admin",
    "roles/artifactregistry.admin",
    "roles/cloudbuild.builds.builder",
    "roles/cloudtrace.agent",
    "roles/compute.admin",
    "roles/container.admin",
    "roles/containerregistry.ServiceAgent",
    "roles/datastore.owner",
    "roles/eventarc.admin",
    "roles/eventarc.eventReceiver",
    "roles/eventarc.serviceAgent",
    "roles/firebase.admin",
    "roles/iam.serviceAccountTokenCreator",
    "roles/iam.serviceAccountUser",
    "roles/iam.workloadIdentityUser",
    "roles/logging.admin",
    "roles/logging.viewer",
    "roles/run.admin",
    "roles/run.invoker",
    "roles/secretmanager.secretAccessor",
    "roles/storage.admin",
    "roles/viewer",
  ] : "${var.project_id}=>${i}"]
  generate_keys = false
}

module "default_sa_iam_bindings" {
  source  = "terraform-google-modules/iam/google//modules/service_accounts_iam"
  project = var.project_id
  mode    = "additive"

  bindings = {
    "roles/compute.admin"                     = local.default_sa_list
    "roles/compute.serviceAgent"              = local.default_sa_list
    "roles/eventarc.admin"                    = local.default_sa_list
    "roles/eventarc.eventReceiver"            = local.default_sa_list
    "roles/eventarc.serviceAgent"             = local.default_sa_list
    "roles/iam.serviceAccountTokenCreator"    = local.default_sa_list
    "roles/iam.serviceAccountUser"            = local.default_sa_list
    "roles/run.admin"                         = local.default_sa_list
    "roles/run.invoker"                       = local.default_sa_list
    "roles/serviceusage.serviceUsageConsumer" = local.default_sa_list
    "roles/storage.admin"                     = local.default_sa_list
  }
}
