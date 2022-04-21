"""
  UJ9 - E2E tests for checking
  HITL endpoint for Rejected documents table
"""

import requests
from endpoint_proxy import get_baseurl


def test_rejected_queue():
  base_url = get_baseurl("hitl-service")
  status="rejected"
  res = requests.post(base_url + f"/hitl_service/v1/get_queue?"\
    f"hitl_status={status}")
  assert res.status_code == 200
