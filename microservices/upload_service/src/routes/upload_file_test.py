"""
  Tests for Upload endpoints
"""
import os
from unittest import mock
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import,consider-using-with
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from common.models import Document
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR

# assigning url
api_url = "http://localhost:8080/upload_service/v1/"
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": STATUS_SUCCESS}

TESTDATA_FILENAME1 = os.path.join(
    os.path.dirname(__file__), "..", "testing", "arkansas-driver-form-5.png")
TESTDATA_FILENAME2 = os.path.join(
    os.path.dirname(__file__), "..", "testing", "Arkansas-form-1.pdf")

TESTDATA_FILENAME3 = os.path.join(
    os.path.dirname(__file__), "..", "testing", "Arkansa-claim-2.pdf")


def creat_mock_data():
  doc = Document()
  doc.case_id = "test123"
  doc.uid = "aSCh3o6BxjPEqjMAQhtC"
  doc.save()
  return doc.uid


def test_upload_json_without_case_id_positive(client_with_emulator):
  with mock.patch("routes.upload_file.create_document_from_data"):
    with mock.patch("routes.upload_file.Logger"):
      response = client_with_emulator.post(
          f"{api_url}upload_json",
          json={
              "name": "Jon",
              "employer_name": "Quantiphi",
              "employer_phone_no": "9282112222",
              "context": "Callifornia",
              "dob": "7 Feb 1997",
              "document_type": "application/ supporting",
              "document_class": "unemployment",
              "ssn": "1234567",
              "phone_no": "9730388333",
              "application_apply_date": "2022/03/16",
              "mailing_address": "Arizona USA",
              "mailing_city": "Phoniex",
              "mailing_zip": "123-33-22",
              "residential_address": "Phoniex , USA",
              "work_end_date": "2022/03",
              "sex": "Female"
          })
      print(response)
  assert response.status_code == 200


def test_upload_json_with_case_id_positive(client_with_emulator):
  with mock.patch("routes.upload_file.create_document_from_data"):
    with mock.patch("routes.upload_file.Logger"):
      response = client_with_emulator.post(
          f"{api_url}upload_json",
          json={
              "case_id": "123A",
              "name": "Jon",
              "employer_name": "Quantiphi",
              "employer_phone_no": "9282112222",
              "context": "Callifornia",
              "dob": "7 Feb 1997",
              "document_type": "application/ supporting",
              "document_class": "unemployment",
              "ssn": "1234567",
              "phone_no": "9730388333",
              "application_apply_date": "2022/03/16",
              "mailing_address": "Arizona USA",
              "mailing_city": "Phoniex",
              "mailing_zip": "123-33-22",
              "residential_address": "Phoniex , USA",
              "work_end_date": "2022/03",
              "sex": "Female"
          })
      print(response)
  assert response.status_code == 200


def test_upload_json_negative(client_with_emulator):
  with mock.patch("routes.upload_file.create_document_from_data"):
    with mock.patch("routes.upload_file.Logger"):
      response = client_with_emulator.post(
          f"{api_url}upload_json",
          json={
              "case_id": "123A",
              "first_name": "Jon",
              "middle_name": "Max",
              "last_name": "Doe",
              "employer_name": "Quantiphi",
              "city": "New York",
              "state": "Callifornia",
              "dob": "7 Feb 1997"
          })
  assert response.status_code == 422


def test_upload_one_pdf_positive(client_with_emulator):
  payload = {}
  mock_uid = creat_mock_data()
  files = [("files", ("Arkansa-claim-2.pdf", open(TESTDATA_FILENAME2,
                                                  "rb"), "application/pdf"))]
  with mock.patch("routes.upload_file.Logger"):
    with mock.patch(
        "routes.upload_file.create_document", return_value=mock_uid):
      with mock.patch("routes.upload_file.publish_document"):
        response = client_with_emulator.post(
            f"{api_url}upload_files"
            f"?context=arkansas&case_id=test123",
            files=files,
            data=payload)
        print(response.text)
  assert response.status_code == 200


def test_upload_files_not_pdf_file(client_with_emulator):
  payload = {}
  files = [("files", ("arkansas-driver-form-5.png",
                      open(TESTDATA_FILENAME1, "rb"), "application/png"))]

  with mock.patch("routes.upload_file.Logger"):
    with mock.patch("routes.upload_file.create_document"):
      with mock.patch("routes.upload_file.publish_document"):
        response = client_with_emulator.post(
            f"{api_url}upload_files"
            f"?context=arkansas&case_id=test123",
            files=files,
            data=payload)
        print(response.text)
  assert response.status_code == 422


def test_upload_one_pdf_without_case_id_positive(client_with_emulator):
  payload = {}
  mock_uid = creat_mock_data()
  files = [("files", ("Arkansa-claim-2.pdf", open(TESTDATA_FILENAME2,
                                                  "rb"), "application/pdf"))]
  with mock.patch("routes.upload_file.Logger"):
    with mock.patch(
        "routes.upload_file.create_document", return_value=mock_uid):
      with mock.patch("routes.upload_file.publish_document"):
        response = client_with_emulator.post(
            f"{api_url}upload_files"
            f"?context=arkansas",
            files=files,
            data=payload)
        print(response.text)
  assert response.status_code == 200


def test_upload_multiple_pdf_without_case_id_positive(client_with_emulator):
  payload = {}
  mock_uid = creat_mock_data()
  files = [("files", ("Arkansa-claim-2.pdf", open(TESTDATA_FILENAME2,
                                                  "rb"), "application/pdf")),
           ("files", ("Arkansas-form-1.pdf", open(TESTDATA_FILENAME3,
                                                  "rb"), "application/pdf"))]

  with mock.patch("routes.upload_file.Logger"):
    with mock.patch(
        "routes.upload_file.create_document", return_value=mock_uid):
      with mock.patch("routes.upload_file.publish_document"):
        response = client_with_emulator.post(
            f"{api_url}upload_files"
            f"?context=arkansas",
            files=files,
            data=payload)
        print(response.text)
  assert response.status_code == 200


def test_upload_multiple_pdf_with_case_id_positive(client_with_emulator):
  payload = {}
  mock_uid = creat_mock_data()
  files = [("files", ("Arkansa-claim-2.pdf", open(TESTDATA_FILENAME2,
                                                  "rb"), "application/pdf")),
           ("files", ("Arkansas-form-1.pdf", open(TESTDATA_FILENAME3,
                                                  "rb"), "application/pdf"))]

  with mock.patch("routes.upload_file.Logger"):
    with mock.patch(
        "routes.upload_file.create_document", return_value=mock_uid):
      with mock.patch("routes.upload_file.publish_document"):
        response = client_with_emulator.post(
            f"{api_url}upload_files"
            f"?context=arkansas&case_id=test123",
            files=files,
            data=payload)
        print(response.text)
  assert response.status_code == 200


def test_upload_multiple_pdf_negative(client_with_emulator):
  payload = {}
  mock_uid = creat_mock_data()
  files = [("files", ("Arkansa-claim-2.pdf", open(TESTDATA_FILENAME2,
                                                  "rb"), "application/pdf")),
           ("files", ("Arkansas-form-1.pdf", open(TESTDATA_FILENAME3,
                                                  "rb"), "application/pdf"))]

  with mock.patch("routes.upload_file.Logger"):
    with mock.patch(
        "routes.upload_file.create_document", return_value=mock_uid):
      with mock.patch("routes.upload_file.publish_document"):
        with mock.patch(
            "routes.upload_file.ug.upload_file", return_value=STATUS_ERROR):
          response = client_with_emulator.post(
              f"{api_url}upload_files"
              f"?context=arkansas&case_id=test123",
              files=files,
              data=payload)
          print(response.text)
  assert response.status_code == 500
