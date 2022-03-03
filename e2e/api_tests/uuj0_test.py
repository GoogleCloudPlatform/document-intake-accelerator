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

def test_upload_api_ping():
  base_url = get_baseurl("classification-service")
  res = requests.get(base_url + "/ping")
  assert res.status_code == 200