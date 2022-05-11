resource "null_resource" "provision" {
    provisioner "local-exec" {
        command = "gcloud builds submit -t gcr.io/${var.project_id}/queue-image ../../../experimental/Queue --gcs-log-dir=gs://${var.project_id}-queue-log"
    }
}
