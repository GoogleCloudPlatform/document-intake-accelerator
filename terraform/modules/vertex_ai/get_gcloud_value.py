#!/bin/python
import os, sys, json, re

# Test this script with the cmd below:
# QUERY_TYPE=endpoints DISPLAY_NAME=classification-endpoint REGION=us-central1 python ../../modules/vertex_ai/get_gcloud_value.py

input = sys.stdin.read()
input_json = json.loads(input) or {}
# input_json = {}

region = input_json.get("region", os.getenv("REGION"))
display_name = input_json.get("display_name", os.getenv("DISPLAY_NAME"))
query_type = input_json.get("query_type", os.getenv("QUERY_TYPE"))

# Sample gcloud cmd:
# gcloud ai endpoints list --region=us-central1 --filter=displayName:classification --quiet --format='json(name)'

cmd = f"gcloud ai {query_type} list --region={region} --filter=displayName:{display_name} --quiet --format='json(name)'"

cmd_output = os.popen(cmd).read()
assert type(cmd_output) == str, f"gcloud output is not a string: {cmd_output}"

cmd_output = re.sub(r"projects.*\/", "", cmd_output)

endpoint_json = json.loads(cmd_output)
endpoint_str = json.dumps(endpoint_json[0])
print(endpoint_str)
