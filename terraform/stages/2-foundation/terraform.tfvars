project_id             = "docai-workflow-dev"
project_number         = "667022277989"
region                 = "us-central1"
storage_multiregion    = "US"
vpc_network            = "default-vpc"
vpc_subnetwork         = "default-vpc-subset"
ip_cidr_range          = "10.0.0.0/16"
master_ipv4_cidr_block = "172.16.0.0/28"
secondary_ranges_pods = {
  range_name    = "secondary-pod-range-01"
  ip_cidr_range = "10.1.0.0/16"
}
secondary_ranges_services = {
  range_name    = "secondary-service-range-01"
  ip_cidr_range = "10.2.0.0/16"
}
