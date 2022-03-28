"""
  Tests format data for bq function
"""
import os
import json
from .format_data_for_bq import format_data_for_bq

# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"

def test_format_data_for_bq():
  input_value = [{"entity":"name","value":"Max"},
                 {"entity":"last_naame","value":"Doe"}
                 ]
  output = format_data_for_bq(input_value)
  expected_output = json.dumps(({"last_naame": "Doe", "name": "Max"}))
  assert output==expected_output

