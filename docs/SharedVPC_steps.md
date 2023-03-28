## Pre-req steps for Shared VPC Setup

- Create Project used for Shared VPC  (HOST_PROJECT_ID)
- Create Project used for the Service (PROJECT_ID)
- Prepare Env Variables:
  ```shell
  export HOST_PROJECT_ID=
  export PROJECT_ID=
  ```
- Run following scripts (will follow instructions as described in [here](docs/NetworkConfiguration.md) and [here](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-shared-vpc)).
  This will create `tier-1` and `tier-2` subnets inside `cda-vpc` network inside the VPC Host Project and grant access for the Service Project:
  ````shell
  gcloud config set project $PROJECT_ID
  bash -e setup/setup_vpc_host_project.sh
  bash -e setup/setup_vpc_service_project.sh
  ````

- Get the IAM policy for the tier-1 subnet:
```shell
gcloud compute networks subnets get-iam-policy tier-1 \
   --project $HOST_PROJECT_ID \
   --region us-central1
```
The output contains an etag field. Make a note of the etag value.
- Create a file named `tier-1-policy.yaml` that has the following content:

- Find our PROJECT_NUMBER of the Service Project:
  ```shell
  SERVICE_PROJECT_NUM=$(gcloud projects describe "$PROJECT_ID" --format='get(projectNumber)')
  ```
- Replace SERVICE_PROJECT_NUM below with the actual value:
  ```shell
  bindings:
  - members:
    - serviceAccount:SERVICE_PROJECT_NUM@cloudservices.gserviceaccount.com
    - serviceAccount:service-SERVICE_PROJECT_NUM@container-engine-robot.iam.gserviceaccount.com
    role: roles/compute.networkUser
  etag: ETAG_STRING
  ```
  
- Set the IAM policy for the tier-1 subnet:
```shell
gcloud compute networks subnets set-iam-policy tier-1 \
    tier-1-policy.yaml \
    --project $HOST_PROJECT_ID \
    --region us-central1
```
- Reserve External Global Static IP (note down the IP) in the Service Project VPC.


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

