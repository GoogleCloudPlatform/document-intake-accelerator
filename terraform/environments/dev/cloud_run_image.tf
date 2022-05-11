resource "null_resource" "provision" {
    provisioner "local-exec" {
        command = "gcloud builds submit -t gcr.io/${var.project_id}/queue-image ../../../cloud-run/Queue --gcs-log-dir=gs://${var.project_id}-queue-log"
    }
}
