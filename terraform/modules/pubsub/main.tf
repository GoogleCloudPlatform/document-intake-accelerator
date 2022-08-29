#Creating a pubsub resource for queue

#creating pubsub topic

resource "google_pubsub_topic" "queue" {
  name = var.topic
}

# # Creating a custom service account for pubsub
# module "pubsub-service-account" {
#     source     = "github.com/terraform-google-modules/cloud-foundation-fabric/modules/iam-service-account/"
#     project_id = var.project_id
#     name       = "pubsub-sa"
#     display_name = "This is service account for pubsub"

#     iam = {
#         "roles/iam.serviceAccountUser" = []
#     }

#     iam_project_roles = {
#         (var.project_id) = [
#             "roles/run.invoker"
#         ]
#     }
# }

#creating pubsub subscription

resource "google_pubsub_subscription" "queue-sub" {
  # depends_on = [
  #   module.pubsub-service-account,
  # ]
  name  = "queue-sub"
  topic = google_pubsub_topic.queue.name

  ack_deadline_seconds       = 600
  message_retention_duration = "86400s"

  expiration_policy {
    ttl = ""
  }

  push_config {
    # Calling the cloud run endpoint
    push_endpoint = var.cloudrun_endpoint
    oidc_token {
      service_account_email = var.service_account_email
    }
  }
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
