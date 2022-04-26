#Creating a cloud run service

resource "google_cloud_run_service" "queue-run" {
  name     = "queue-cloudrun"
  location = var.region

  template {
    spec {
      containers {
        image = var.cloud_run_image_path
        ports{
            container_port=8000
        }
        env {
          name = "t"
          value = "10"
        }
       
      }
      service_account_name = module.cloud-run-service-account.email
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
    }
}

#Retriving cloudrun endpoint

output "cloud_run" {
    value = google_cloud_run_service.queue-run.status[0].url
}
