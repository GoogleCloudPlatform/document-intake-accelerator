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

# Eventarc to trigger start-pipeline
variable "project_id" {
  type        = string
  description = "project ID"
}

variable "gcs_bucket" {
  type        = string
  description = "bucket for PA forms for batch processing"
}

variable "topic" {
  type        = string
  description = "topic"
}

variable "cloudrun_name" {
  type        = string
  description = "cloudrun_name"
}

variable "cloudrun_location" {
  type        = string
  description = "cloudrun_location"
}

variable "cloudrun_endpoint" {
  type        = string
  description = "cloudrun_endpoint"
}

variable "region" {
  type        = string
  description = "region"
}

variable "service_account_email" {
  type = string
}
