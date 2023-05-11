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

from typing import List, Dict
from common.models.document import Document
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR


def is_processing_success(data: List[Dict]):
  """Checks if the document is processed and went through all the
     stages successfully

  Args:
      data (List[Dict]): List of uploaded documents

  Returns:
      Bool: Returns a boolean value if document processing is successful or not
  """
  d = Document()
  is_processed = False
  for doc in data:
    uid = doc.get("uid")
    details = d.find_by_uid(uid)
    status = details.system_status
    print("System status is: ", status)
    stages = [
        "uploaded", "classification", "extraction", "auto_approval",
        "validation", "matching"
    ]
    if status is not None:
      for stat in status:
        is_processed = stat.get("stage") in stages and stat.get(
            "status") == STATUS_SUCCESS
  return is_processed


def is_autoapproved(uid: str):
  """Checks if the document is processed and went through all the
     stages successfully after reassign and last stage is
     autoapproved

  Args:
      data (List[Dict]): List of uploaded documents

  Returns:
      Bool: Returns a boolean value if document processing is successful or not
  """
  d = Document()
  is_processed = False
  details = d.find_by_uid(uid)
  status = details.system_status
  print("System status is: ", status)
  stages = ["auto_approval"]
  if status is not None:
    for stat in status:
      is_processed = stat.get("stage") in stages and stat.get(
          "status") == STATUS_SUCCESS
  return is_processed
