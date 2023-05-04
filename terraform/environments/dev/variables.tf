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

variable "project_id" {
  type        = string
  description = "GCP Project ID"

  validation {
    condition     = length(var.project_id) > 0
    error_message = "The project_id value must be an non-empty string."
  }
}

variable "dataset_id" {
  type        = string
  description = "Dataset ID"
  validation {
    condition     = length(var.dataset_id) > 0
    error_message = "The dataset_id value must be an non-empty string."
  }
}

variable "docai_project_id" {
  type        = string
  description = "GCP Project ID where DocAI processors will be deployed"

  validation {
    condition     = length(var.docai_project_id) > 0
    error_message = "The project_id value must be an non-empty string."
  }
}

variable "iap_secret_name" {
  type        = string
  default = "cda-iap-secret"
}

variable "region" {
  type        = string
  description = "GCP Region"
  default     = "us-central1"

  validation {
    condition     = length(var.region) > 0
    error_message = "The region value must be an non-empty string."
  }
}

variable "firestore_region" {
  type        = string
  description = "Firestore Region"
  default     = "us-central"
}

variable "dataset_location" {
  type        = string
  description = "BigQuery Dataset location"
  default     = "US"
}

variable "multiregion" {
  type    = string
  default = "us"
}

variable "env" {
  type    = string
  default = "dev"
}

variable "cluster_name" {
  type    = string
  default = "main-cluster"
}

variable "network_config" {
  description = "Shared VPC network configurations to use. If null networks will be created in projects with preconfigured values."
  type = object({
    host_project      = string
    network           = string
    subnet            = string
    serverless_subnet = string
    region            = string
    gke_secondary_ranges = object({
      pods     = string
      services = string
    })
  })
  default = null
}

variable "cda_external_ip" {
  type        = string
  description = "External Reserved IP address for the UI"
  default     = null
}

variable "internal_ip_name" {
  type    = string
  default = "cda-internal-ip"
}

variable "network" {
  type    = string
  default = "default-vpc"
}

variable "secondary_ranges_pods" {
  type = object({
    range_name    = string
    ip_cidr_range = string
  })

  default = {
    range_name    = "secondary-pod-range-01"
    ip_cidr_range = "10.1.0.0/16"
  }
}

variable "secondary_ranges_services" {
  type = object({
    range_name    = string
    ip_cidr_range = string
  })
  default = {
    range_name    = "secondary-service-range-01"
    ip_cidr_range = "10.2.0.0/16"
  }
}

variable "subnetwork" {
  type    = string
  default = "cde-subnetwork-01"
}

variable "serverless_subnet" {
  type    = string
  default = "cda-subnet"
}

variable "vpc_connector_name" {
  type    = string
  default = "cda-vpc-serverless"
}

#adding new variables for the updated scripts

variable "project_name" {
  type        = string
  default     = ""
  description = "This project name"
}

variable "org_id" {
  default     = ""
  description = "This project organization id"
}

variable "firebase_init" {
  default     = false
  description = "Whether to run Firebase init resource"
}

variable "cloudrun_deploy" {
  default     = false
  description = "Whether to deploy Queue cloudrun service resource"
}

variable "admin_email" {
  type        = string
  description = "email of the cert issuer"
}

variable "api_domain" {
  type        = string
  description = "api domain name"
}

variable "config_bucket" {
  type        = string
  description = "Bucket to store solution configuration files"
}

variable "service_account_name_gke" {
  type        = string
  default     = "gke-sa"
  description = "Service account name for the GKE node."
  # This service account will be created in both GCP and GKE, and will be
  # used for workload federation in all microservices.
}

variable "master_ipv4_cidr_block" {
  type        = string
  description = "The IP range in CIDR notation to use for the hosted master network"
  default     = "172.16.0.0/28"
}

variable "cda_external_ui" {
  type        = bool
  description = "Expose UI to public internet"
  default     = false
}