#Creating a pubsub resource for queue

resource "google_pubsub_topic" "queue" {
  name = "queue-topic"
}

resource "google_pubsub_subscription" "queue-sub" {
  name  = "queue-sub"
  topic = google_pubsub_topic.queue.name

  ack_deadline_seconds = 600
  message_retention_duration = "86400s"



  expiration_policy {
    ttl = ""
  }

  push_config {
    push_endpoint = google_cloud_run_service.queue-run.status[0].url
    oidc_token {
        service_account_email = module.pubsub-service-account.email
    }
  }

}
