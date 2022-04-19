"""
  UJ15 - E2E tests for checking
  HITL endpoint for document review
"""

import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
#Accessing ping endpoint for sample service

def test_fetch_api():
  base_url = get_baseurl("hitl-service")
  case_id = "769f79df-bf25-11ec-a675-43fd64c79606"
  uid = "aSCh3o6BxjPEqjMAQhtC"
  res = requests.get(base_url + f"/hitl_service/v1/fetch_file?case_id={case_id}&uid={uid}")
  assert res.status_code == 200


def test_get_document_api():
  d = Document()
  d.uid = "e2e_test_uid"
  d.case_id = "e2e_test_caseid"
  d.context = "arkansas"
  d.save()
  uid = "e2e_test_uid"
  base_url = get_baseurl("hitl-service")
  res = requests.get(base_url + f"/hitl_service/v1/get_document?uid={uid}")
  assert res.status_code == 200
