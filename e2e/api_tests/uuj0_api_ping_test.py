"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
  UUJO - E2E tests for checking
  microservice endpoints
  are accessible
"""

import requests
from endpoint_proxy import get_baseurl

#Accessing ping endpoint for sample service

def test_api_ping():
  base_url = get_baseurl("sample-service")
  res = requests.get(base_url + "/ping")
  assert res.status_code == 200

#Accessing api endpoint for sample service which does not exist

def test_non_exist_endpoint():
  base_url = get_baseurl("sample-service")
  res = requests.get(base_url + "/sample-service/not-exist")
  print(base_url)
  assert res.status_code == 404


def test_upload_api_ping():
  base_url = get_baseurl("upload-service")
  res = requests.get(base_url + "/ping")
  assert res.status_code == 200

def test_classification_api_ping():
  base_url = get_baseurl("classification-service")
  res = requests.get(base_url + "/ping")
  assert res.status_code == 200

def test_extraction_api_ping():
  base_url = get_baseurl("extraction-service")
  res = requests.get(base_url + "/ping")
  assert res.status_code == 200

def test_validation_api_ping():
  base_url = get_baseurl("validation-service")
  res = requests.get(base_url + "/ping")
  assert res.status_code == 200

def test_hitl_service_ping():
  base_url = get_baseurl("hitl-service")
  res = requests.get(base_url + "/ping")
  assert res.status_code == 200

def test_document_status_service_ping():
  base_url = get_baseurl("document-status-service")
  res = requests.get(base_url + "/ping")
  assert res.status_code == 200


def test_matching_service_ping():
  base_url = get_baseurl("matching-service")
  res = requests.get(base_url + "/ping")
  assert res.status_code == 200