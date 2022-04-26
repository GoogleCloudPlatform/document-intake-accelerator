#Creating custom VPC Network and Subnet

resource "google_compute_subnetwork" "custom-vpc" {
  name          = var.subnetwork
  ip_cidr_range = "10.255.0.0/16"
  region        = "us-central1"
  network       = google_compute_network.custom-test.id
  secondary_ip_range {
    range_name    = "tf-pod-secondary-range-update1"
    ip_cidr_range = "10.52.0.0/14"
  }
  secondary_ip_range {
    range_name    = "tf-service-secondary-range-update1"
    ip_cidr_range = "10.56.0.0/20"
  }

}


resource "google_compute_network" "custom-test" {
  name                    = var.network
  auto_create_subnetworks = false
}