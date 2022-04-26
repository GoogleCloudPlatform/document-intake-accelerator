# Instantiate firestore on environment
resource "google_app_engine_application" "firestore" {
  provider      = google
  location_id   = var.firestore_region
  database_type = "CLOUD_FIRESTORE"
}