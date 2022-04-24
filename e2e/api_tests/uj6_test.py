"""
  UJ6 - E2E tests for checking
  HITL endpoint for table data
  is working
"""

import datetime
import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document

def add_records():
  """
  Function to insert records into collection that can be fetched by the API
  """
  timestamp = str(datetime.datetime.utcnow())
  d = Document()
  d.case_id = "uj6_table_test_1"
  d.uid = "uj6_table_test_1"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.system_status = [{
    "stage":"uploaded",
    "status":"success",
    "timestamp":timestamp
  }]
  d.save()
  
def test_all_table_data():
  """
  User journey to see all document records in the table
  """
  #Adding records
  add_records()
  
  #Get base url for hitl service
  base_url = get_baseurl("hitl-service")
  
  res = requests.get(base_url + "/hitl_service/v1/report_data")
  
  #Checking if response status was 200
  assert res.status_code == 200
  
  #Getting json data from response
  res_data = res.json()
  print(res_data)
  
  #Checking that the response data is not empty
  assert res_data["len"] > 0
  assert res_data["data"] is not []
