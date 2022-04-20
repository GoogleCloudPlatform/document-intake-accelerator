"""
  Tests for validation endpoints
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from unittest import mock
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from common.models import Document

# assigning url
API_URL = "http://localhost:8080/validation_service/v1/validation/"

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": "Success"}


def test_validation_api(client_with_emulator):
  """Test case to check the validation endpoint"""
  doc = Document()
  doc.case_id = "5-ui"
  doc.uid = "aSCh3o6BxjPEqjMAQhtC"
  doc.document_class = "driving_license"
  doc.save()
  entities = [{"value": "A-60544059",
               "extraction_confidence": 0.94,
               "manual_extraction": False,
               "entity": "dl_no",
               "corrected_value": None,
               "matching_score": None,
               "validation_score": None},
              {"value": "1992-04-07",
               "entity": "dob",
               "corrected_value": None,
               "extraction_confidence": 0.73,
               "manual_extraction": False,
               "matching_score": None,
               "validation_score": 0.0}, ]
  url = f"{API_URL}validation_api?case_id=5-ui&uid=aSCh3o6BxjPEqjMAQhtC&" \
    "doc_class=driving_license"
  with mock.patch("routes.validation.update_validation_status"):
    with mock.patch("routes.validation.get_values"):
      with mock.patch("routes.validation.Logger"):
        response = client_with_emulator.post(url,json =entities )
  assert response.status_code == 200, "Status 200"


def test_validation_api_invalid_doc_class(client_with_emulator):
  """Test case to check the validation endpoint
  when invalid document class is provided"""
  doc = Document()
  doc.case_id = "5-ui"
  doc.uid = "aSCh3o6BxjPEqjMAQhtC"
  doc.save()
  entities = [{"value": "A-60544059",
               "extraction_confidence": 0.94,
               "manual_extraction": False,
               "entity": "dl_no",
               "corrected_value": None,
               "matching_score": None,
               "validation_score": None},
              {"value": "1992-04-07",
               "entity": "dob",
               "corrected_value": None,
               "extraction_confidence": 0.73,
               "manual_extraction": False,
               "matching_score": None,
               "validation_score": 0.0}, ]
  url = f"{API_URL}validation_api?case_id=5-ui&uid=aSCh3o6BxjPEqjMAQhtC&"\
    "doc_class=invalid_class"
  with mock.patch("routes.validation.update_validation_status"):
    with mock.patch("routes.validation.Logger"):
      response = client_with_emulator.post(url,json = entities)
  assert response.status_code == 500, "Status 500"
