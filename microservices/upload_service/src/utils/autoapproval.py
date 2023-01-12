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

"""
This code is Used to check the approval status of a document
depending on the 3 different scores
"""
import os
import json
from google.cloud import storage
from common.config import STATUS_APPROVED, STATUS_REVIEW, STATUS_REJECTED, STATUS_PENDING, STATUS_ERROR
from common.autoapproval_config import AUTO_APPROVAL_MAPPING
from common.utils.logging_handler import Logger


def get_autoapproval_status(validation_score, extraction_score, matching_score,
                            document_label, document_type):
  """
  Used to calculate the approval status of a document depending on the
  validation, extraction and Matching Score
  Input:
  validation_score : Validation Score
  extraction_score : Extraction Score
  matching_score : Matching Score
  Output:
  status : Accept/Reject or Review
  flag : Yes or no
  """

  data = AUTO_APPROVAL_MAPPING

  Logger.info(f"Validation_Score:{validation_score}, Extraction_score :"
              f"{extraction_score},Matching_Score:{matching_score},"
              f"DocumentLabel:{document_label},DocumentType:{document_type}")
  flag = "no"

  if document_label not in data.keys():
    status = STATUS_REVIEW
    print(f"Auto-approval is not configured for {document_label}")
    return status, flag

  if document_type in ("supporting_documents", "claims_form"):
    if document_type == "claims_form":
      if extraction_score == 0.0:
        flag = "no"
        status = STATUS_REVIEW
        return status, flag

    for i in data[document_label]:
      if i != "Reject":
        v_limit = data[document_label][i]["Validation_Score"]
        e_limit = data[document_label][i]["Extraction_Score"]
        m_limit = data[document_label][i]["Matching_Score"]
        print(v_limit, e_limit, m_limit)

        if (validation_score > v_limit and extraction_score > e_limit and
            matching_score > m_limit):
          flag = "yes"
          status = STATUS_APPROVED
          return status, flag

      else:
        v_limit = data[document_label][i]["Validation_Score"]
        e_limit = data[document_label][i]["Extraction_Score"]
        m_limit = data[document_label][i]["Matching_Score"]
        flag = "no"

        if (validation_score > v_limit and extraction_score > e_limit and
            matching_score > m_limit):
          status = STATUS_REVIEW
          Logger.info(f"Status :{status}")
          return status, flag

        else:
          status = STATUS_REJECTED
          Logger.info(f"Status :{status}")
          return status, flag

  elif document_type == "application_form":
    if extraction_score == 0.0:
      flag = "no"
      status = STATUS_REVIEW
      return status, flag

    for i in data[document_label]:
      if i != "Reject":
        e_limit = data[document_label][i]["Extraction_Score"]
        if extraction_score > e_limit:
          flag = "yes"
          status = STATUS_APPROVED
          Logger.info(f"Status :{status}")
          return status, flag

      else:
        e_limit = data[document_label][i]["Extraction_Score"]
        flag = "no"
        if extraction_score > e_limit:
          status = STATUS_REVIEW
          Logger.info(f"Status :{status}")
          return status, flag

        else:
          status = STATUS_REJECTED
          Logger.info(f"Status :{status}")
          return status, flag

  else:
    status = STATUS_REVIEW
    Logger.info(f"Status :{status}")
    return status, flag
