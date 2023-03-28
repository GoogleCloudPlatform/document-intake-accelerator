## Pre-req steps for Shared VPC Setup

- Create Project used for Shared VPC 
- Create Project used for the Service 
- Prepare Env Variables:
  ```shell
  export HOST_PROJECT_ID=
  export PROJECT_ID=
  ```
- Run following scripts (will follow instructions as described in [here](docs/NetworkConfiguration.md)):


```shell
gcloud config set project $PROJECT_ID
bash setup_host_vpc_project.sh
bash setup/setup_vpc_shared_project.sh
```

- Reserve External Global Static IP (note down the IP)

- Prepare `terraform/environments/dev/terraform.tfvars`
  - `cp terraform/environments/dev/terraform.sample.tfvars terraform/environments/dev/terraform.tfvars`
  - Fill in parameters




### Setup


- Purchase Domain, register DNS record tie it to the reserved external IP
- Cloud Domain:
  - Enable Cloud Domains API
  - Register Domain
- Cloud DNS:
  - Enable Cloud DNS API
  - Create Zone

