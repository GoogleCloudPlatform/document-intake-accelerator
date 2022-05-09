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