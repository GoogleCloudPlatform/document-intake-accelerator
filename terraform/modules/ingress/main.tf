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

# Terraform Block
terraform {
  required_providers {
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.14.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.7.0"
    }
  }
}

locals {
  ip_name = (
    var.external_ip_name != null
    ? var.external_ip_name
    : google_compute_address.ingress_ip_address[0].name
  )
}

# Todo - replace with GCP Managed Certificates
module "cert_manager" {
  source = "terraform-iaac/cert-manager/kubernetes"

  cluster_issuer_email                   = var.cert_issuer_email
  cluster_issuer_name                    = "letsencrypt"
  cluster_issuer_private_key_secret_name = "cert-manager-private-key"
}


resource "google_compute_address" "ingress_ip_address" {
  count        = var.external_address == null ? 1 : 0
  project      = var.project_id # Service Project ID
  name         = "ingress-ip"
  address_type = "EXTERNAL"
}


resource "kubernetes_ingress_v1" "default_ingress" {
  metadata {
    name = "default-ingress"
    annotations = {
      "kubernetes.io/ingress.class"                 = "gce"
      "kubernetes.io/ingress.global-static-ip-name" = local.ip_name
      //      "cert-manager.io/cluster-issuer"                     = module.cert_manager.cluster_issuer_name
      //      "nginx.ingress.kubernetes.io/enable-cors"            = "true"
      //      "nginx.ingress.kubernetes.io/cors-allow-methods"     = "PUT,GET,POST,DELETE,OPTIONS"
      //      "nginx.ingress.kubernetes.io/cors-allow-origin"      = var.cors_allow_origin
      //      "nginx.ingress.kubernetes.io/cors-allow-credentials" = "true"
      //      "nginx.ingress.kubernetes.io/proxy-read-timeout"     = "3600"
    }
  }

  spec {
    # Default backend to UI app.
    default_backend {
      service {
        name = "adp-ui"
        port {
          number = 80
        }
      }
    }

    rule {
      host = var.domain
      http {
        # Upload Service
        path {
          backend {
            service {
              name = "upload-service"
              port {
                number = 80
              }
            }
          }
          path_type = "Prefix"
          path      = "/upload_service"
        }

        # classification Service
        path {
          backend {
            service {
              name = "classification-service"
              port {
                number = 80
              }
            }
          }
          path_type = "Prefix"
          path      = "/classification_service"
        }

        # validation Service
        path {
          backend {
            service {
              name = "validation-service"
              port {
                number = 80
              }
            }
          }
          path_type = "Prefix"
          path      = "/validation_service"
        }

        # extraction Service
        path {
          backend {
            service {
              name = "extraction-service"
              port {
                number = 80
              }
            }
          }
          path_type = "Prefix"
          path      = "/extraction_service"
        }

        # hitl Service
        path {
          backend {
            service {
              name = "hitl-service"
              port {
                number = 80
              }
            }
          }
          path_type = "Prefix"
          path      = "/hitl_service"
        }

        # document-status Service
        path {
          backend {
            service {
              name = "document-status-service"
              port {
                number = 80
              }
            }
          }
          path_type = "Prefix"
          path      = "/document_status_service"
        }

        # matching Service
        path {
          backend {
            service {
              name = "matching-service"
              port {
                number = 80
              }
            }
          }
          path = "/matching_service"
        }

        # Config Service
        path {
          backend {
            service {
              name = "config-service"
              port {
                number = 80
              }
            }
          }
          path_type = "Prefix"
          path      = "/config_service"
        }
      }
    }

    tls {
      hosts = [
        var.domain,
      ]
      secret_name = "cert-manager-private-key"
    }
  }
}
