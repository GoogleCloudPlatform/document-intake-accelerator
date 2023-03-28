#!/usr/bin/env bash

export CLOUD_ROUTER_NAME=cda-router
export CLOUD_NAT_NAME=cda-nat
export REGION=us-central1
export FW_RULE_NAME=fw-i-a-gkemaster-gkeworkers-tcp-8443-webhook
export MASTER_IPV4_CIDR="172.16.0.0/28" # default range if not changed in terraform.tfvars
export GKE_NETWORK_TAG=gke-main-cluster

export NETWORK=cda-vpc
export SUBNET1=tier-1
export SUBNET2=tier-2

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