"""
  UJ16 - E2E tests for download functionality
"""

import requests
from endpoint_proxy import get_baseurl

def test_download_document_api():
  base_url = get_baseurl("hitl-service")
  case_id = "769f79df-bf25-11ec-a675-43fd64c79606"
  uid = "aSCh3o6BxjPEqjMAQhtC"
  res = requests.get(base_url + f"/hitl_service/v1/fetch_file?"\
    f"case_id={case_id}&uid={uid}&download={True}")
  assert res.status_code == 200
