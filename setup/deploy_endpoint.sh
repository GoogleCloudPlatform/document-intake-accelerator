#!/usr/bin/env bash
FQDN="cda.endpoints.${PROJECT_ID}.cloud.goog"
K8S_NAME=cda-service
K8S_INGRESS_IP=$1

if [ -z "$K8S_INGRESS_IP" ]; then
  echo "must provide Reserved IP address as a parameter"
fi

echo "Deploying end point ${FQDN} with reserved IP $K8S_INGRESS_IP"
cat <<EOF > ${K8S_NAME}-openapi.yaml
swagger: "2.0"
info:
  description: "$K8S_NAME"
  title: "$K8S_NAME"
  version: "1.0.0"
host: "${FQDN}"
x-google-endpoints:
- name: "${FQDN}"
  target: "$K8S_INGRESS_IP"
paths: {}

EOF

gcloud endpoints services deploy ${K8S_NAME}-openapi.yaml
rm ${K8S_NAME}-openapi.yaml
export API_DOMAIN=${FQDN}
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}"/../SET