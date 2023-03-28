## Pre-req steps for Shared VPC Setup

- Create Project used for Shared VPC and create VPC inside with subnetwork following these [instructions](docs/NetworkConfiguration.md) 
  - Create NAT and Router
- Create Service Project

```shell
export HOST_PROJECT_ID=
export PROJECT_ID=
export API_DOMAIN=mydomain.com
```

```shell
gcloud config set project $PROJECT_ID
bash setup/setup_vpc_shared_project.sh
```

- Reserve External Global Static IP (note down the IP)

- Prepare `terraform/environments/dev/terraform.tfvars`
  - `cp terraform/environments/dev/terraform.sample.tfvars terraform/environments/dev/terraform.tfvars`
  - Fill in parameters




- Go to VPC Host Project -> Shared VPC page
  - Attach Service Project to the VPC Host Project (Kubernetes Engine access - must be checked in)
  - Select all subnetworks
  - Other parameters can be left default
- Grant required permissions for the Service project to access Host Project [instructions](docs/NetworkConfiguration.md)





### Setup


- Purchase Domain, register DNS record tie it to the reserved external IP
- Cloud Domain:
  - Enable Cloud Domains API
  - Register Domain
- Cloud DNS:
  - Enable Cloud DNS API
  - Create Zone

