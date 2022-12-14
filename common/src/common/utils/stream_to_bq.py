"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

""" Bigquery claim inserts,updates and deletes """
import copy
import json
from .logging_handler import Logger
from common.config import PROJECT_ID, DATABASE_PREFIX ,BIGQUERY_DB

def stream_claim_to_bigquery(client, claim_dict, operation, timestamp):
  table_id = f"{PROJECT_ID}.{DATABASE_PREFIX}rules_engine.claims"
  new_claim_dict = copy.deepcopy(claim_dict)
  del new_claim_dict["document_details"]
  new_claim_dict["operation"] = operation
  new_claim_dict["timestamp"] = timestamp
  new_claim_dict["created_timestamp"] = timestamp
  new_claim_dict["last_updated_timestamp"] = timestamp
  new_claim_dict["all_document_details"] = json.dumps(
      claim_dict.get("document_details"))
  rows_to_insert = [new_claim_dict]
  # Make an API request
  errors = client.insert_rows_json(table_id, rows_to_insert)
  if errors == []:
    Logger.info("New rows have been added.")
  elif isinstance(errors, list):
    error = errors[0].get("errors")
    Logger.error(f"Encountered errors while inserting rows: {error}")


def delete_claim_in_bigquery(client, claim_id, timestamp):
  table_id = f"{PROJECT_ID}.{DATABASE_PREFIX}rules_engine.claims"
  claim_dict = {}
  claim_dict["claim_id"] = claim_id
  claim_dict["operation"] = "DELETE"
  claim_dict["timestamp"] = timestamp
  claim_dict["created_timestamp"] = timestamp
  claim_dict["last_updated_timestamp"] = timestamp
  rows_to_insert = [claim_dict]
  # Make an API request
  errors = client.insert_rows_json(table_id, rows_to_insert)
  if errors == []:
    Logger.info("New rows have been added.")
  elif isinstance(errors, list):
    error = errors[0].get("errors")
    Logger.error(f"Encountered errors while inserting rows: {error}")

def stream_document_to_bigquery(client, case_id ,uid,
  document_class , document_type, entites):
  """
    Function insert's data in Bigquery database
    Args :
      entity : string format of enties and values
      case_id : str
      uid : str
      document_class : str
      document_type: str
    output :
      if successfully executed : returns []
      if fails : returns error
  """
  table_id = f"{PROJECT_ID}.{DATABASE_PREFIX}{BIGQUERY_DB}"
  rows_to_insert= [
    {"case_id":case_id,
    "uid":uid,
    "document_class":document_class ,
    "document_type":document_type,
    "entities":entites}
  ]
  errors = client.insert_rows_json(table_id, rows_to_insert)
  if errors == []:
    Logger.info(f"New rows have been added for "
                f"case_id {case_id} and {uid}")
  elif isinstance(errors, list):
    error = errors[0].get("errors")
    Logger.error(f"Encountered errors while inserting rows "
                 f"for case_id {case_id} and uid {uid}: {error}")
  return errors
