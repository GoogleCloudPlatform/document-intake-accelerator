declare -a EnvVars=(
  "PROJECT_ID"
  "REGION"
)
for variable in ${EnvVars[@]}; do
  if [[ -z "${!variable}" ]]; then
    input_value=""
    while [[ -z "$input_value" ]]; do
      read -p "Enter the value for ${variable}: " input_value
      declare "${variable}=$input_value"
    done
  fi
done

gcloud container clusters describe main-cluster \
    --region=${REGION} \
    --format="get(privateClusterConfig.publicEndpoint)"
