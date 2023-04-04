//network_config = {
//  host_project      = "HOST_PROJECT_ID"
//  network = "cda-vpc"   #SHARED_VPC_NETWORK_NAME"
//  subnet  = "tier-1"    #SUBNET_NAME
//  serverless_subnet = "serverless-subnet"
//  gke_secondary_ranges = {
//    pods     = "tier-1-pods"       #SECONDARY_SUBNET_PODS_RANGE_NAME
//    services = "tier-1-services"   #SECONDARY_SUBNET_SERVICES_RANGE_NAME"
//  }
//  region = "us-central1"
//}
cda_external_ui = true       # Expose UI to the Internet: true or false
cda_external_ip = "cda-ip"   # Name of the reserved IP address. Must be reserved in the Service Project, Global IP address
//master_ipv4_cidr_block = "172.16.0.0/28" # MASTER.CIDR/28  When using a different cidr block, make sure to add a firewall rule on port 8443 (see setup/setup_vpc_host_project.sh)
