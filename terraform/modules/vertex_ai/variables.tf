variable "project_id" {
  type        = string
  description = "project ID"
}

variable "region" {
  type = string
}

variable "model_gcs_path" {
  type = string
}

variable "model_name" {
  type = string
}

variable "image_uri" {
  type = string
}

variable "accelerator_param" {
  type    = string
  default = ""
}
