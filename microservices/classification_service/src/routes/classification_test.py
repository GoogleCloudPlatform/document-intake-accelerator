"""
  Tests for classification endpoints
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore

from urllib import request, response
from unittest.mock import patch
# assigning url
api_url = "http://localhost:8080/classification_service/v1/classification/classification_api"

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": "Success"}

def call_to_classify_all_parameters():
  response = request.post(f"{api_url}?case_id=%20123&uid=5fd0e97e-9dea-11ec-8e64-da7c2efe947f&gcs_url=gs%3A%2F%2Fdocument-upload-test%2F%20123%2F5fd0e97e-9dea-11ec-8e64-da7c2efe947f%2Ffuture-genral.pdf")
  return response

def call_to_classify_no_case_id():
  response = request.post(f"{api_url}?case_id=&uid=5fd0e97e-9dea-11ec-8e64-da7c2efe947f&gcs_url=gs%3A%2F%2Fdocument-upload-test%2F%20123%2F5fd0e97e-9dea-11ec-8e64-da7c2efe947f%2Ffuture-genral.pdf")
  return response


def call_to_classify_no_uid():
  response = request.post(f"{api_url}?case_id=%20123&uid=&gcs_url=gs%3A%2F%2Fdocument-upload-test%2F%20123%2F5fd0e97e-9dea-11ec-8e64-da7c2efe947f%2Ffuture-genral.pdf")
  return response

def call_to_classify_invalid_gcs_uri():
  response = request.post(f"{api_url}?case_id=%20123&uid=&gcs_url=gs%3A%2F%2Fdocument-upload-test%2F%20123%2F5fd0e97e-9dea-11ec-8e64-da7c2efe947f%2Ffuture-genral.")
  return response


def test_classify_all_parameters(client_with_emulator):
  """
    Test to check the classification endpoint with all endpoints
  """
  response_data = {"case_id": " 123", "u_id": "5fd0e97e-9dea-11ec-8e64-da7c2efe947f", "predicted_class": "UE", "model_conf": 0.880875826, "model_endpoint_id": "3512649929430401024"}
  with patch('routes.classification_test.call_to_classify_all_parameters',return_value = response_data):
    response = call_to_classify_all_parameters()
    assert response == response

def test_classify_with_missing_parameters_caseid(client_with_emulator):
  """
    Test to check the classification endpoint with empty case_id
  """
  response_data = {"detail" : {
    "status" : "Failed",
    "message" : "Parameter Missing"
  }}
  
  with patch('routes.classification_test.call_to_classify_no_case_id',return_value = response_data):
    response = call_to_classify_no_case_id()
    assert response["detail"]["status"] == "Failed"

def test_classify_with_missing_parameters_uid(client_with_emulator):
  """
    Test to check the classification endpoint with empty uid
  """
  
  response_data = {"detail" : {
    "status" : "Failed",
    "message" : "Parameter Missing"
  }}

  with patch('routes.classification_test.call_to_classify_no_uid',return_value = response_data):
    response = call_to_classify_no_uid()
    assert response["detail"]["status"] == "Failed"

def test_classify_with_invalid_gcs_uri(client_with_emulator):
  """
    Test to check the classification endpoint with invalid gcs uri
  """
  response_data = {"detail" : {
    "status" : "Failed",
    "message" : "Invalid gcs uri path"
  }}

  with patch('routes.classification_test.call_to_classify_invalid_gcs_uri',return_value = response_data):
    response = call_to_classify_invalid_gcs_uri()
    assert response["detail"]["status"] == "Failed"
