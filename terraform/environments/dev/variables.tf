variable "project_id" {
  type        = string
  description = "GCP Project ID"
  default     = "claims-processing-dev"

  validation {
    condition     = length(var.project_id) > 0
    error_message = "The project_id value must be an non-empty string."
  }
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
  type        = string
  default     = "us"
}

variable "env" {
  type        = string
  default     = "dev"
}

variable "network" {
    type = string
    default = "adp-vpc"
}

variable "subnetwork" {
    type = string
    default = "adp-subnetwork"  
}

#adding new variables for the updated scripts

variable "cloud_run_image_path" {
    type = string
    default = "gcr.io/claims-processing-dev/queue-image"
}


variable "dataset_name" {
    type = string
    default = "entity_extraction"
    description = "bigquery dataset"
}

variable "table_name" {
    type = string
    default = "entity"
    description = "bigquery table"
}

variable "project_name" {
    type = string
    default = ""
    description = "This project name"
}

variable "org_id" {
    default = ""
    description = "This project organization id"
  
}
