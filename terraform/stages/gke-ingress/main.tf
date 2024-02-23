/**
 * Copyright 2023 Google LLC
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

# project-specific locals
locals {
  cda_external_ui           = data.terraform_remote_state.foundation.outputs.cda_external_ui
  internal_ip_name          = data.terraform_remote_state.foundation.outputs.internal_ip_name

  addresses = "http://localhost:4200,http://localhost:3000,http://${var.api_domain},https://${var.api_domain}"
  cors_origin = (
    var.cda_external_ip == null
    ? local.addresses
    : "${local.addresses},http://${var.cda_external_ip},https://${var.cda_external_ip}"
  )
}

data "google_project" "project" {}


data "terraform_remote_state" "foundation" {
  backend = "gcs"
  config = {
    bucket = "${var.project_id}-tfstate"
    prefix = "stage/foundation"
  }
}

module "ingress" {
  source            = "../../modules/ingress"
  project_id        = var.project_id
  cert_issuer_email = var.admin_email

  # Domains for API endpoint, excluding protocols.
  cda_external_ui   = local.cda_external_ui
  domain            = var.api_domain
  region            = var.region
  cors_allow_origin = local.cors_origin
  external_ip_name  = var.cda_external_ip
  internal_ip_name  = local.internal_ip_name
}
