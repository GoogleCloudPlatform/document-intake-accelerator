#Creating a firbase project

resource "google_project" "default" {
  provider = google-beta

  project_id = var.project_id
  name       = var.project_name
  org_id     = var.org_id
}

resource "google_firebase_project" "firebase_project" {
  provider = google-beta
  project  = google_project.default.project_id
}