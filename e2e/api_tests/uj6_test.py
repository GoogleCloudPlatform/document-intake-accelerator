"""
  UUJ6 - E2E tests for checking
  HITL endpoint for table data
  is working
"""

import requests
from endpoint_proxy import get_baseurl

#Accessing ping endpoint for sample service

def test_api_ping():
  base_url = get_baseurl("hitl-service")
  res = requests.get(base_url + "/report_data")
  assert res.status_code == 200
