# Enabling a firbase project

resource "google_app_engine_application" "firebase_init" {
  provider = google-beta
  project  = var.project_id
  location_id = var.firestore_region
  database_type = "CLOUD_FIRESTORE"
}

resource "google_storage_bucket" "firestore-backup-bucket" {
  name          = "${local.project_id}-firestore-backup"
  location      = local.multiregion
  storage_class = "NEARLINE"

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 356
    }
    action {
      type = "Delete"
    }
  }
}

# give backup SA rights on bucket
resource "google_storage_bucket_iam_binding" "firestore_sa_backup_binding" {
  bucket = google_storage_bucket.firestore-backup-bucket.name
  role   = "roles/storage.admin"
  members = [
    "serviceAccount:${local.project_id}@appspot.gserviceaccount.com",
  ]
  depends_on = [
    google_app_engine_application.firebase_init
  ]
}
