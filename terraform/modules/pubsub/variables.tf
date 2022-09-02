variable "project_id" {
  type        = string
  description = "project ID"
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
