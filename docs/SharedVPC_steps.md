## Setting up Shared VPC

Refer to this [guide](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-shared-vpc) for in-detail  information on setting up shared VPC.

## Prerequisite  steps for Shared VPC Setup

- Create Project used for Shared VPC  (HOST_PROJECT_ID)
- Create Project used for the Service (PROJECT_ID)
- Prepare Env Variables:
  ```shell
  export HOST_PROJECT_ID=
  export PROJECT_ID=
  ```
- Run following scripts (will follow instructions as described [here](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-shared-vpc)).
  This will create `tier-1` and `tier-2` subnets inside `cda-vpc` network of the VPC Host Project and grant access for the Service Project. `tier-1` subnet will have two secondary ranges for GKE services `tier-1-services` and GKE pods `tier-1-pods`:
  ````shell
  gcloud config set project $PROJECT_ID
  bash -e setup/setup_vpc_host_project.sh
  bash -e setup/setup_vpc_service_project.sh
  ````


## Troubleshooting
Failure while deploying Ingress: 

```
│ Error: timed out waiting for the condition
│
│   with module.ingress.module.nginx-controller.helm_release.application,
│   on .terraform/modules/ingress.nginx-controller/main.tf line 1, in resource "helm_release" "application":
│    1: resource "helm_release" "application" {
│
```
Resolution:
- Make sure that there is a firewall rule allowing Master Node communicate with the worker Nodes:
  - Ingress allowed for the network from MASTER_IPV4_CIDR on port 8443

> master-ipv4-cidr Specifies an internal IP address range for the control plane (For more details read about [private cluster](https://cloud.google.com/kubernetes-engine/docs/how-to/private-clusters).)
> 
In the example below, MASTER_IPV4_CIDR is 172.1.1.0/28
![](firewall-rule-gkemaster.png)