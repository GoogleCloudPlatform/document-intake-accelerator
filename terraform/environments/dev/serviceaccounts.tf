#Service account for gke

module "gke-node-cluster-service-account" {
    source     = "github.com/terraform-google-modules/cloud-foundation-fabric/modules/iam-service-account/"
    project_id = var.project_id
    name       = "${var.project_id}-sa-node"
    display_name = "This is service account for gke to access other services"

    # authoritative roles granted *on* the service accounts to other identities


    iam = {
        "roles/iam.serviceAccountUser" = []
    }

    # non-authoritative roles granted *to* the service accounts on other resources

    iam_project_roles = {
        (var.project_id) = [
            "roles/monitoring.viewer",
            "roles/monitoring.metricWriter",
            "roles/logging.logWriter",
            "roles/stackdriver.resourceMetada.writer",
            "roles/storage.admin",
            "roles/containerregistry.ServiceAgent"
        ]
    }
}

module "gke-pod-service-account" {
  source       = "github.com/terraform-google-modules/cloud-foundation-fabric/modules/iam-service-account/"
  project_id   = var.project_id
  name         = "${var.project_id}-sa-pod"
  display_name = "The GKE Pod worker service account. Most microservices run as this."

  # authoritative roles granted *on* the service accounts to other identities
  iam = {
    "roles/iam.serviceAccountUser" = []
  }
  # non-authoritative roles granted *to* the service accounts on other resources
  iam_project_roles = {
    (var.project_id) = [
      "roles/firebase.admin",
      "roles/bigquery.admin",
      "roles/datastore.owner",
      "roles/datastore.importExportAdmin",
      "roles/storage.objectAdmin",
      "roles/storage.admin",
      "roles/secretmanager.secretAccessor",
      # Granting Workload Identity User to SA for GKE -> CloudSQL requests
      "roles/iam.workloadIdentityUser",
      # Granting Dataflow Admin and Dataflow Worker for Fraud Jobs
      "roles/dataflow.admin",
      "roles/dataflow.worker",
    ]
  }
}

# Creating a Kubernetes Service account for Workload Identity
resource "kubernetes_service_account" "ksa" {
  metadata {
    name = "ksa"
    annotations = {
      "iam.gke.io/gcp-service-account" = module.gke-pod-service-account.email
    }
  }
}

# Enable the IAM binding between your YOUR-GSA-NAME and YOUR-KSA-NAME:
resource "google_service_account_iam_binding" "gsa-ksa-binding" {
  service_account_id = module.gke-pod-service-account.service_account.id
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog"
  ]

  depends_on = [kubernetes_service_account.ksa]
}



#Creating a custom service account for pubsub

module "pubsub-service-account" {
    source     = "github.com/terraform-google-modules/cloud-foundation-fabric/modules/iam-service-account/"
    project_id = var.project_id
    name       = "${var.project_id}-sapub"
    display_name = "This is service account for pubsub"

    iam = {
        "roles/iam.serviceAccountUser" = []
    }

    iam_project_roles = {
        (var.project_id) = [
            "roles/run.invoker"
        ]
    }
}

#creating a custom service account for cloud run

module "cloud-run-service-account" {
    source     = "github.com/terraform-google-modules/cloud-foundation-fabric/modules/iam-service-account/"
    project_id = var.project_id
    name       = "run-${var.project_id}-sar"
    display_name = "This is service account for cloud run"

    iam = {
        "roles/iam.serviceAccountUser" = []
    }

    iam_project_roles = {
        (var.project_id) = [
            "roles/run.invoker",
            "roles/eventarc.eventReceiver",
            "roles/firebase.admin",
            "roles/firestore.serviceAgent"
        ]
    }
}
