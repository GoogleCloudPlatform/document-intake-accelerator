# Enabling a firbase project

resource "google_app_engine_application" "app" {
  provider = google-beta
  project  = google_project.default.project_id
  location_id = var.region
  database_type = "CLOUD_FIRESTORE"
}
