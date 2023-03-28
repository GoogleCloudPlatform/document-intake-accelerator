## Setting up Shared VPC

Refer to this [guide](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-shared-vpc) for in-detail  information on setting up shared VPC.

Things to check are listed below.

Make sure to add service project as attached to the VPC Hosted Project.
When enabling host project, and attaching service projects, Under Kubernetes Engine access, make sure to check Enabled checkbox.

```shell
export HOST_PROJECT_ID=
export PROJECT_ID=
```

The command that you use depends on the [required administrative role](https://cloud.google.com/vpc/docs/shared-vpc#iam_roles_required_for_shared_vpc) that you have.
If you have Shared VPC Admin role at the organizational level:
```shell
gcloud compute shared-vpc associated-projects add $PROJECT_ID \
    --host-project $HOST_PROJECT_ID
```
If you have Shared VPC Admin role at the folder level:
```shell
gcloud beta compute shared-vpc associated-projects add $PROJECT_ID \
    --host-project $HOST_PROJECT_ID
```
If the `network_config` variable is not provided, one VPC will be created in the project.

##Enable APIs

Make sure that the GKE API (`container.googleapis.com`) is enabled in the VPC host project.
```shell
gcloud services enable container.googleapis.com --project $HOST_PROJECT_ID     
gcloud services enable container.googleapis.com --project $PROJECT_ID     
```


##Grant Required Roles
```shell
export HOST_PROJECT_ID=<Your Host Project ID here>
export SERVICE_PROJECT_NUM=$(gcloud projects describe "$PROJECT_ID" --format='get(projectNumber)')
```
```shell
gcloud projects add-iam-policy-binding $HOST_PROJECT_ID \
    --member serviceAccount:service-$SERVICE_PROJECT_NUM@container-engine-robot.iam.gserviceaccount.com \
    --role=roles/container.hostServiceAgentUser
gcloud projects add-iam-policy-binding $HOST_PROJECT_ID \
    --member=serviceAccount:service-$SERVICE_PROJECT_NUM@container-engine-robot.iam.gserviceaccount.com \
    --role=roles/compute.securityAdmin
gcloud projects add-iam-policy-binding $HOST_PROJECT_ID \
    --member=serviceAccount:service-$SERVICE_PROJECT_NUM@container-engine-robot.iam.gserviceaccount.com \
    --role=roles/compute.networkUser  
gcloud projects add-iam-policy-binding $HOST_PROJECT_ID \
    --member=serviceAccount:$SERVICE_PROJECT_NUM@cloudservices.gserviceaccount.com \
    --role=roles/compute.networkUser
       
```

##Network and Subnetwork Requirements for GKE
- Pods secondary range for pods and services is required to be of size  /24 for the max_pods_per_node.
- For the general requirements of the IP address ranges for nodes, Pods and Services, please refer [here](https://cloud.google.com/kubernetes-engine/docs/concepts/alias-ips)

Here is a [working example](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-shared-vpc#console) of a subnetwork inside shared VPC network for GKE:
- Create subnet `SUBNET_NAME`: For IPv4 range of the subnet, enter 10.0.4.0/22.
- Create two secondary subnets for gke pods and services Ip ranges:
    - `SECONDARY_SUBNET_SERVICES`: For Secondary IPv4 range, enter 10.0.32.0/20.
    - `SECONDARY_SUBNET_PODS`: For Secondary IPv4 range, enter 10.4.0.0/14.

## Setting up NAT and Router

Because we are using private cluster without external IP address, it is important that SharedVPC Project has Cloud NAT, Cloud Router and FW rules.

Below are the commands to add that:
```shell
export HOST_PROJECT_ID=
export NETWORK=
```

```shell
export CLOUD_ROUTER_NAME=cda-router
export CLOUD_NAT_NAME=cda-nat
export REGION=us-central1
export FW_RULE_NAME=fw-i-a-gkemaster-gkeworkers-tcp-8443-webhook
export MASTER_IPV4_CIDR="172.16.0.0/28" # default range if not changed in terraform.tfvars
export GKE_NETWORK_TAG=gke-main-cluster
```

```shell
gcloud compute routers create $CLOUD_ROUTER_NAME \
--project=$HOST_PROJECT_ID \
--network=$NETWORK \
--region=$REGION

gcloud compute routers nats create $CLOUD_NAT_NAME \
--router=$CLOUD_ROUTER_NAME \
--region=$REGION \
--auto-allocate-nat-external-ips \
--nat-all-subnet-ip-ranges \
--project $HOST_PROJECT_ID \
--enable-logging

gcloud compute firewall-rules create $FW_RULE_NAME \
--action=ALLOW \
--direction=INGRESS \
--network=$NETWORK \
--source-ranges=$MASTER_IPV4_CIDR \
--target-tags $GKE_NETWORK_TAG \
--rules=tcp:8443 \
--project $HOST_PROJECT_ID
```

