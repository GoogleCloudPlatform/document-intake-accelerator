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
    google = {
      source  = "hashicorp/google"
      version = "~>4.0"
    }
  }
}

locals {
  external_ip_name = (
  var.external_ip_name == null && var.cda_external_ui == true
  ? google_compute_global_address.ingress_ip_address[0].name
  : var.external_ip_name
  )

  cda_external_ui = var.cda_external_ui

}

# External Ingress

# TODO: switch to hashicorp k8s provider, use side by side
# k2tf
resource "kubectl_manifest" "managed_certificate" {
  count     = var.cda_external_ui == true ? 1 : 0
  yaml_body = <<YAML
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: gclb-managed-cert
spec:
  domains:
    - ${var.domain}
YAML
}

resource "google_compute_global_address" "ingress_ip_address" {
  count        = var.external_ip_name == null && var.cda_external_ui == true ? 1 : 0
  project      = var.project_id # Service Project ID
  name         = "ingress-ip"
  address_type = "EXTERNAL"
}

resource "kubectl_manifest" "frontend_config" {
  count     = var.cda_external_ui == true ? 1 : 0
  yaml_body = <<YAML
apiVersion: networking.gke.io/v1beta1
kind: FrontendConfig
metadata:
  name: ingress-security-config
spec:
  sslPolicy: ${google_compute_ssl_policy.gke-ingress-ssl-policy[0].name}
  redirectToHttps:
    enabled: true
YAML
}

resource "google_compute_ssl_policy" "gke-ingress-ssl-policy" {
  count           = var.cda_external_ui == true ? 1 : 0
  name            = "gke-ingress-ssl-policy"
  profile         = "MODERN"
  min_tls_version = "TLS_1_2"
}

resource "kubernetes_ingress_v1" "external_ingress" {
  count = var.cda_external_ui == true ? 1 : 0
  metadata {
    name = "external-ingress"
    annotations = {
      "kubernetes.io/ingress.class"                 = "gce"
      "kubernetes.io/ingress.global-static-ip-name" = local.external_ip_name
      "networking.gke.io/managed-certificates"      = kubectl_manifest.managed_certificate[0].name
      "networking.gke.io/v1beta1.FrontendConfig"    = kubectl_manifest.frontend_config[0].name
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

  }
}

# Internal Ingress

resource "kubernetes_ingress_v1" "internal_ingress" {
  count = var.cda_external_ui == false ? 1 : 0
  metadata {
    name = "internal-ingress"
    annotations = {
      "kubernetes.io/ingress.class"                   = "gce-internal"
      "kubernetes.io/ingress.regional-static-ip-name" = var.internal_ip_name
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

  }
}
