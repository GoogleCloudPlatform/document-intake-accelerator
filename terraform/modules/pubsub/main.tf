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
  labels = {
    goog-packaged-solution = "prior-authorization"
  }
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
