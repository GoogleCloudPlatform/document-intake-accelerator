# Enabling a firbase project

resource "google_app_engine_application" "firebase_init" {
  provider = google-beta
  project  = var.project_id
  location_id = var.firestore_region
  database_type = "CLOUD_FIRESTORE"
}
