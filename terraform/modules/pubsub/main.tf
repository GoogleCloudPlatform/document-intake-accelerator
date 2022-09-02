#Creating a pubsub resource for queue

#creating pubsub topic
resource "google_pubsub_topic" "queue" {
  name = var.topic
}

resource "google_eventarc_trigger" "queue-topic-trigger" {
  provider        = google-beta
  name            = "queue-topic-trigger"
  project         = var.project_id
  location        = var.region
  service_account = var.service_account_email

  matching_criteria {
    attribute = "type"
    value     = "google.cloud.pubsub.topic.v1.messagePublished"
  }
  destination {
    cloud_run_service {
      service = var.cloudrun_name
      region  = var.cloudrun_location
      path    = "/queue/publish"
    }
  }
  transport {
    pubsub {
      topic = google_pubsub_topic.queue.name
    }
  }
}
