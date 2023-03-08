/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

#Creating a pubsub resource for start pipeline

##creating pubsub topic
#resource "google_pubsub_topic" "queue" {
#  name = var.topic
#}

#resource "google_eventarc_trigger" "queue-topic-trigger" {
#  provider        = google-beta
#  name            = "queue-topic-trigger"
#  project         = var.project_id
#  location        = var.region
#  service_account = var.service_account_email
#
#  matching_criteria {
#    attribute = "type"
#    value     = "google.cloud.pubsub.topic.v1.messagePublished"
#  }
#  destination {
#    cloud_run_service {
#      service = var.cloudrun_name
#      region  = var.cloudrun_location
#      path    = "/queue/publish"
#    }
#  }
#  transport {
#    pubsub {
#      topic = google_pubsub_topic.queue.name
#    }
#  }
#}

#Creating a pubsub resource for start-pipeline

#creating pubsub topic
#resource "google_pubsub_topic" "start-pipeline" {
#  name = var.topic
#}

# Define a Cloud Run service as an event target
#resource "google_cloud_run_service" "default" {
#  provider = google-beta
#  name     = "cloudrun-hello-tf"
#  location = "us-east1"
#
#  template {
#    spec {
#      containers {
#        image = "gcr.io/cloudrun/hello"
#      }
#    }
#  }
#
#  traffic {
#    percent         = 100
#    latest_revision = true
#  }
#
#}


resource "google_eventarc_trigger" "pipeline-topic-trigger" {
  provider        = google-beta
  name            = "startpipeline-topic-trigger"
  project         = var.project_id
  location        = var.region
  service_account = var.service_account_email
  labels = {
    goog-packaged-solution = "prior-authorization"
  }
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.storage.object.v1.finalized"
  }
  matching_criteria {
    attribute = "bucket"
    value     = var.gcs_bucket
  }
  destination {
    cloud_run_service {
      service = var.cloudrun_name
      region  = var.cloudrun_location
      path    = "/start-pipeline/run"
    }
  }
#  transport {
#    pubsub {
#      topic = google_pubsub_topic.start-pipeline.name
#    }
#  }
}