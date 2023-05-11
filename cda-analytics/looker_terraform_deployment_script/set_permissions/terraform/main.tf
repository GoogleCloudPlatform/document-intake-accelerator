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
    dataset = "custom_fhir_flattened_views"
    patient_view = "hde_accelerator_patient_flow_view"
    health_equity_view = "hde_accelerator_health_equity_view"
    transfer_of_care_view = "hde_accelerator_transition_of_care_view"
    health_equity_patient_view = "hde_accelerator_health_equity_patient_view"
}
# Service account and permissions for BQ flattened views
resource "google_service_account" "custom_fhir_flattened_views_sa" {
  account_id   = "hde-accelerator-bq-sa"
  display_name = "hde-accelerator-bq-sa"
  project = var.project_id
}
resource "google_bigquery_dataset_iam_member" "custom_fhir_flattened_views_editor" {
  project = var.project_id 
  dataset_id = local.dataset
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.custom_fhir_flattened_views_sa.email}"
}

# Adding required roles to service accounts
resource "google_project_iam_member" "custom_fhir_flattened_views_binding" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.custom_fhir_flattened_views_sa.email}"
  depends_on = [
    google_service_account.custom_fhir_flattened_views_sa
  ]
}

# creating looker_scratch dataset and applying permissions
resource "google_bigquery_dataset" "looker_scratch" {
  project = var.project_id
  dataset_id                  = "looker_scratch"
  friendly_name               = "looker_scratch"
 
}

resource "google_bigquery_dataset_iam_binding" "editor" {
  project = var.project_id
  dataset_id = google_bigquery_dataset.looker_scratch.dataset_id
  role       = "roles/bigquery.dataEditor"

  members = [
    "serviceAccount:${google_service_account.custom_fhir_flattened_views_sa.email}"
  ]
}