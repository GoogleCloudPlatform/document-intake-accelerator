resource "null_resource" "provision" {
  provisioner "local-exec" {
    command = "gcloud builds submit -t gcr.io/${var.project_id}/queue-image ../../../cloud_run/Queue --gcs-log-dir=gs://${var.project_id}-queue-log --set-env-vars='API_DOMAIN=${var.api_domain}'"
  }
}
