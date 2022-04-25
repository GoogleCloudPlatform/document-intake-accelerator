"""
  E2E test case for download by HITL functionality
"""

import requests
from endpoint_proxy import get_baseurl

def test_download_document_api():
  """"User journey to download a document"""
  #Getting base url
  base_url = get_baseurl("hitl-service")
  case_id = "769f79df-bf25-11ec-a675-43fd64c79606"
  uid = "aSCh3o6BxjPEqjMAQhtC"

  #Checking if the request was successful
  res = requests.get(base_url + f"/hitl_service/v1/fetch_file?"\
    f"case_id={case_id}&uid={uid}&download={True}")
  assert res.status_code == 200
  assert res.headers["content-disposition"].split(";")[0] == "attachment"
