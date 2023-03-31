#!/usr/bin/env bash

export CLOUD_ROUTER_NAME=cda-router
export CLOUD_NAT_NAME=cda-nat
export REGION=us-central1
export FW_RULE_NAME=fw-i-a-gkemaster-gkeworkers-tcp-8443-webhook

# default range if not changed in terraform.tfvars
# When changed, needs also to be updated in  terraform.tfvars, since needs a firewall rule for master node to communicate with the nodes.
export MASTER_IPV4_CIDR="172.16.0.0/28"

export GKE_NETWORK_TAG=gke-main-cluster

export NETWORK=cda-vpc
export SUBNET1=tier-1
export SUBNET2=tier-2
export SUBNET3=serverless-subnet

gcloud services enable container.googleapis.com --project $HOST_PROJECT_ID
gcloud compute networks create $NETWORK \
    --subnet-mode custom \
    --project $HOST_PROJECT_ID

gcloud compute networks subnets create $SUBNET1 \
    --project $HOST_PROJECT_ID \
    --network $NETWORK \
    --range 10.0.4.0/22 \
    --region us-central1 \
    --secondary-range tier-1-services=10.0.32.0/20,tier-1-pods=10.4.0.0/14

gcloud compute networks subnets create $SUBNET2 \
    --project $HOST_PROJECT_ID \
    --network $NETWORK \
    --range 172.16.4.0/22 \
    --region us-central1 \
    --secondary-range tier-2-services=172.16.16.0/20,tier-2-pods=172.20.0.0/14

gcloud compute networks subnets create $SUBNET3 \
    --project $HOST_PROJECT_ID \
    --network=$NETWORK \
    --range=10.8.0.0/28 \
    --region=us-central1

gcloud compute networks subnets create proxy-only-subnet \
    --project $HOST_PROJECT_ID \
    --purpose=REGIONAL_MANAGED_PROXY \
    --role=ACTIVE \
    --region=us-central1 \
    --network=$NETWORK \
    --range=10.129.0.0/23
  
#If you have Shared VPC Admin role at the organizational level:
gcloud compute shared-vpc enable $HOST_PROJECT_ID

#If you have Shared VPC Admin role at the folder level:
# gcloud beta compute shared-vpc enable $HOST_PROJECT_ID


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

gcloud compute firewall-rules create serverless-to-vpc-connector \
  --allow tcp:667,udp:665-666,icmp \
  --source-ranges 107.178.230.64/26,35.199.224.0/19 \
  --direction=INGRESS \
  --target-tags vpc-connector \
  --network=$NETWORK \
  --project $HOST_PROJECT_ID

  
gcloud compute firewall-rules create vpc-connector-to-serverless \
  --allow tcp:667,udp:665-666,icmp \
  --destination-ranges 107.178.230.64/26,35.199.224.0/19 \
  --direction=EGRESS \
  --target-tags vpc-connector \
  --network=$NETWORK\
  --project $HOST_PROJECT_ID
  
  
gcloud compute firewall-rules create vpc-connector-health-checks \
  --allow tcp:667 \
  --source-ranges 130.211.0.0/22,35.191.0.0/16,108.170.220.0/23 \
  --direction=INGRESS \
  --target-tags vpc-connector \
  --network=$NETWORK\
  --project $HOST_PROJECT_ID

  gcloud compute firewall-rules create allow-proxy-connection \
    --allow=TCP \
    --source-ranges=10.129.0.0/23 \
    --network=$NETWORK\
    --project $HOST_PROJECT_ID
