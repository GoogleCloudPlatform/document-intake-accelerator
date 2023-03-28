## Pre-req steps for Shared VPC Setup

- Create Project used for Shared VPC  (HOST_PROJECT_ID)
- Create Project used for the Service (PROJECT_ID)
- Prepare Env Variables:
  ```shell
  export HOST_PROJECT_ID=
  export PROJECT_ID=
  ```
- Run following scripts (will follow instructions as described in [here](docs/NetworkConfiguration.md)):

  ````shell
  gcloud config set project $PROJECT_ID
  bash -e setup/setup_host_vpc_project.sh
  bash -e setup/setup_vpc_shared_project.sh
  ````

- Reserve External Global Static IP (note down the IP) in the Service Project VPC (TODO: Find out how to reserve IP in the Host VPC project and make that work)


- Prepare `terraform/environments/dev/terraform.tfvars`
  ```shell
  cp terraform/environments/dev/terraform.sample.tfvars terraform/environments/dev/terraform.tfvars
  ```
  - Uncomment and fill in parameters for host_project (HOST_PROJECT_ID) and cda_external_ip (With reserved External IP)


```shell
export API_DOMAIN=mydomain.com
export DOCAI_PROJECT_ID=
./init.sh
```

