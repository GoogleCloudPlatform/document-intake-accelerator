#Creating gke cluster and nodes

resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.region

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  network = google_compute_network.custom-test.self_link
  subnetwork = google_compute_subnetwork.custom-vpc.self_link
  initial_node_count       = 1
  ip_allocation_policy {
    cluster_secondary_range_name = google_compute_subnetwork.custom-vpc.secondary_ip_range.0.range_name
    services_secondary_range_name = google_compute_subnetwork.custom-vpc.secondary_ip_range.1.range_name
  }
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
}


resource "google_container_node_pool" "primary_nodes" {
  name       = var.nodes_name
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 1

  node_config {
    machine_type = var.machine_type

    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    service_account = module.gke-node-cluster-service-account.email
    oauth_scopes    = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
  upgrade_settings {
    max_surge    = 3
    max_unavailable =0
  }
}




