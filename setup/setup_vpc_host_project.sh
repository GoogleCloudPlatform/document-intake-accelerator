#!/bin/bash
# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/../SET
export CLOUD_ROUTER_NAME=cda-router
export CLOUD_NAT_NAME=cda-nat

export FW_RULE_NAME=fw-i-a-gkemaster-gkeworkers-tcp-8443-webhook

# default range if not changed in terraform.tfvars
# When changed, needs also to be updated in  terraform.tfvars, since needs a firewall rule for master node to communicate with the nodes.
export MASTER_IPV4_CIDR="172.16.0.0/28"

export GKE_NETWORK_TAG=gke-main-cluster

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