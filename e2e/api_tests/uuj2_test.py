import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
BUCKET_NAME = "gs://document-upload-test"

def test_uuj_5():
  """
    UUJ 5 - Process the uploaded application form
    1. Classify the document
    2. Perform extraction on the classified document
    3. Autoapprove
  """
  case_id = "test123_x2"
  uid="tI03AfAUpwZECYd5f6OM"
  file = "Copy of Arkansas-form-1.pdf"
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
  print("==================classification successful in uuj5===================")
#   Run extraction for the document
  d.document_class = "unemployment_form"
  d.document_type = "application_form"
  d.save()
  extraction_url = get_baseurl("extraction-service")
  response = requests.post(extraction_url+f"/extraction_service/v1/extraction_api?case_id={case_id}&uid={uid}&doc_class=unemployment_form&document_type=application_form&context=arkansas&gcs_url={gcs_url}")
  assert response.status_code == 200
  print("==================extraction successful in uuj5===================")
#  Run autoapproval
  dsu_url = get_baseurl("document-status-service")
  response = requests.post(dsu_url+f"/document_status_service/v1/update_autoapproved_status?case_id={case_id}&uid={uid}&status=success&autoapproved_status=Approved&is_autoapproved=yes")
  assert response.status_code == 200
  print("==================autoapproval successful in uuj5===================")