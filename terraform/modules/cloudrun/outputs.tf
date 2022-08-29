output "endpoint" {
  value = google_cloud_run_service.cloudrun-service.status[0].url
}

output "name" {
  value = google_cloud_run_service.cloudrun-service.name
}

output "location" {
  value = google_cloud_run_service.cloudrun-service.location
}
