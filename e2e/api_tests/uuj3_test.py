import requests
import traceback
from endpoint_proxy import get_baseurl
from common.models.document import Document
BUCKET_NAME = "gs://document-upload-test"

def test_uuj_6():
  """
    UUJ 6 - Process the uploaded Supporting Document
    1. Classify the document
    2. Perform extraction
    3. Perform validation
    4. Perform matching
    3. Autoapprove
  """
  
  case_id = "test123_x2"
  uid="4snA7fAT15S6qSXtuqE2"
  file = "arkansas-paystub-1.pdf"
  gcs_url = f"{BUCKET_NAME}/{case_id}/{uid}/{file}"
  d = Document()
  d.uid = uid
  d.case_id = case_id
  d.context = "arkansas"
  d.url = gcs_url
  d.save()
#   Run classification
  classification_url = get_baseurl("classification-service")
  response = requests.post(classification_url+f"/classification_service/v1/classification/classification_api?case_id={case_id}&uid={uid}&gcs_url={gcs_url}")
  assert response.status_code == 200
  print("==================classification successful in uuj6===================")
#   Run extraction for the document
  d.document_class = "pay_stub"
  d.document_type = "supporting_documents"
  d.save()
  extraction_url = get_baseurl("extraction-service")
  response = requests.post(extraction_url+f"/extraction_service/v1/extraction_api?case_id={case_id}&uid={uid}&doc_class=pay_stub&document_type=supporting_documents&context=arkansas&gcs_url={gcs_url}")
  assert response.status_code == 200
  print("==================extraction successful in uuj6===================")
  entities = [{"entity": "employer_address", "value": "261 Jeffrey Prairie North Carolstad, VA 25512", "extraction_confidence": 0.6, "manual_extraction": False, "corrected_value": None}, {"entity": "employer_name", "value": "EARNINGS STATEMENT", "extraction_confidence": None, "manual_extraction": True, "corrected_value": None}, {"entity": "hours", "value": "160", "extraction_confidence": None, "manual_extraction": True, "corrected_value": None}, {"entity": "name", "value": "DAVID WILSON", "extraction_confidence": 0.9, "manual_extraction": False, "corrected_value": None}, {"entity": "pay_date", "value": "2021-11-01", "extraction_confidence": 0.94, "manual_extraction": False, "corrected_value": None}, {"entity": "pay_period_from", "value": "2021-10-01", "extraction_confidence": 0.6, "manual_extraction": False, "corrected_value": None}, {"entity": "pay_period_to", "value": "2021-10-31", "extraction_confidence": 0.73, "manual_extraction": False, "corrected_value": None}, {"entity": "rate", "value": "35", "extraction_confidence": None, "manual_extraction": True, "corrected_value": None}, {"entity": "ssn", "value": "198-10-2003", "extraction_confidence": 0.73, "manual_extraction": False, "corrected_value": None}, {"entity": "ytd", "value": "24362.21", "extraction_confidence": 0.93, "manual_extraction": False, "corrected_value": None}]
#  Run validation for the document
  validation_url = get_baseurl("validation-service")
  response = requests.post(validation_url+f"/validation_service/v1/validation/validation_api?case_id={case_id}&uid={uid}" \
    f"&doc_class=pay_stub",json=entities)
  assert response.status_code == 200
  print("==================validation successful in uuj6===================")
#  Run Matching for the document
  matching_url = get_baseurl("matching-service")
  response = requests.post(matching_url+f"/matching_service/v1/match_document?case_id={case_id}&uid={uid}")
  assert response.status_code == 200
  print("==================matching successful in uuj6===================")
#  Run autoapproval
  dsu_url = get_baseurl("document-status-service")
  response = requests.post(dsu_url+f"/document_status_service/v1/update_autoapproved_status?case_id={case_id}&uid={uid}&status=success&autoapproved_status=Rejected&is_autoapproved=yes")
  assert response.status_code == 200
  print("==================autoapproval successful in uuj6===================")
