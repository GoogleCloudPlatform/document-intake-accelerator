#creating trigger for cloudrun when document is uploaded to pubsub topic

resource "google_eventarc_trigger" "trigger-pubsub-tf" {
  provider = google-beta
  name     = "trigger-pubsub-tf"
  project = var.project_id
  location = google_cloud_run_service.queue-run.location
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.pubsub.topic.v1.messagePublished"
  }
  service_account = module.pubsub-service-account.email
  destination {
    cloud_run_service {
      service = google_cloud_run_service.queue-run.name
      region  = google_cloud_run_service.queue-run.location
    }
  }
  transport {
    pubsub {
        topic = google_pubsub_topic.queue.name
    }
  }
}
