variable "project_id" {
  type        = string
  description = "project ID"
}

variable "processors" {
  type        = any
}

variable "multiregion" {
  type    = string
  default = "us"
}
