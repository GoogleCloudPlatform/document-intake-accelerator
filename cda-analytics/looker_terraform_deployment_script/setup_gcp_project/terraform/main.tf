/**
* Copyright 2022 Google LLC
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*      http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

locals {
  roles = [
    "roles/file.editor",
    "roles/cloudkms.admin",
    "roles/redis.admin",
    "roles/cloudsql.admin",
    "roles/compute.admin",
    "roles/compute.networkAdmin",
    "roles/dns.admin",
    "roles/iam.workloadIdentityPoolAdmin",
    "roles/secretmanager.viewer",
    "roles/container.admin",
    "roles/resourcemanager.projectIamAdmin",
    "roles/secretmanager.secretAccessor",
    "roles/iam.serviceAccountAdmin",
    "roles/iam.serviceAccountUser",
    "roles/servicenetworking.networksAdmin",
    "roles/storage.admin",
    "roles/storage.objectViewer",
    "roles/logging.logWriter"
  ]
}

module "secret_manager" {
  source = "github.com/GoogleCloudPlatform/cloud-foundation-fabric/modules/secret-manager"

  project_id = var.project_id
  secrets = {
    looker_license_key = null
    looker_db_pw       = null
    gcm_key            = null
  }
}

module "artifact_registry" {
  source = "github.com/GoogleCloudPlatform/cloud-foundation-fabric/modules/artifact-registry"

  project_id = var.project_id
  location   = var.location
  format     = "DOCKER"
  id         = var.repository_id
}

module "service_account" {
  source = "github.com/GoogleCloudPlatform/cloud-foundation-fabric/modules/iam-service-account"

  project_id = var.project_id
  name       = var.sa_name
  iam_project_roles = {
    "${var.project_id}" = local.roles
  }
  #impersonification of SA enabling
  iam = {
    "roles/iam.serviceAccountTokenCreator" = ["user:${var.email_address}"]
  }
}

resource "google_project_iam_member" "cloudbuild" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}

module "dns" {
  source = "github.com/GoogleCloudPlatform/cloud-foundation-fabric/modules/dns"

  project_id = var.project_id
  type       = "public"
  name       = replace(trim(var.dns_domain, "."), ".", "-")
  domain     = var.dns_domain
}
