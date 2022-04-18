"""
  UUJ6 - E2E tests for checking
  HITL endpoint for table data
  is working
"""

import requests
from endpoint_proxy import get_baseurl

#Accessing ping endpoint for sample service

def test_report_data_api():
  base_url = get_baseurl("hitl-service")
  res = requests.get(base_url + "/hitl_service/v1/report_data")
  assert res.status_code == 200
