"""
  User uploads apllication in the form of JSON data

"""
import requests
from endpoint_proxy import get_baseurl


def test_upload_json_data():
  """
   User uploads JSON application in json payload
  """
  upload_base_url = get_baseurl("upload-service")
  payload = {
    "case_id": "123A",
    "name": "William",
    "employer_name": "Quantiphi",
    "employer_phone_no": "9282112222",
    "context": "Callifornia",
    "dob": "7 Feb 1997",
    "document_type": "application_form",
    "document_class": "unemployment_form",
    "ssn": "1234567",
    "phone_no": "9730388333",
    "application_apply_date": "2022/03/16",
    "mailing_address": "Arizona USA",
    "mailing_city": "Phoniex",
    "mailing_zip": "123-33-22",
    "residential_address": "Phoniex , USA",
    "work_end_date": "2022/03",
    "sex": "Female"
  }
  response_app = requests.post(
    f"{upload_base_url}/upload_service/v1/upload_json",
    json =  payload)
  response_app.status_code = 200

