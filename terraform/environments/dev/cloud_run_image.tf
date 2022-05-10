resource "null_resource" "provision" {
    provisioner "local-exec" {
        command = "gcloud builds submit -t gcr.io/claims-processing-dev/queue-image ../../../experimental/Queue --gcs-log-dir=gs://${var.project_id}-queue-log"
    }
}
