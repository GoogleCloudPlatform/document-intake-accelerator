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

locals {
  domain = join(".", slice(split(".", var.api_domain), 1, length(split(".", var.api_domain))))
  name = join("-", split(".", local.domain))
  record_name = join("", slice(split(".", var.api_domain), 0, 1))
  network_selflink = data.google_compute_network.my-network.self_link
  subnet_selflink = data.google_compute_subnetwork.my-subnetwork.self_link
}

data "google_compute_network" "my-network" {
  name    = var.vpc_network
  project = var.network_project_id
}

data "google_compute_subnetwork" "my-subnetwork" {
  name   = var.vpc_subnetwork
  project = var.network_project_id
  region = var.region
}

resource "google_compute_address" "internal-ip" {
  project      = var.project_id
  region       = var.region
  name         = var.internal_ip_name
  address_type = "INTERNAL"
  subnetwork   = local.subnet_selflink
}

module "dns-cda-private-zone" {
  source  = "terraform-google-modules/cloud-dns/google"
  version = "4.2.1"
  project_id = var.project_id
  type       = "private"
  name       = local.name
  domain     = "${local.domain}."

  private_visibility_config_networks = [
    local.network_selflink
  ]

  recordsets = [
    {
      name    = local.record_name
      type    = "A"
      ttl     = 300
      records = [
        google_compute_address.internal-ip.address
        ,
      ]
    },
  ]
}
