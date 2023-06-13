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

from common.models import Document

""" extraction endpoints """

from fastapi import APIRouter, HTTPException


from common.utils.logging_handler import Logger
from common.config import STATUS_SUCCESS, STATUS_ERROR, DocumentWrapper
from models.process_task import ProcessTask
from utils.extract_entities import extract_entities

import traceback
from fastapi import BackgroundTasks

# disabling for linting to pass
# pylint: disable = broad-except
router = APIRouter()

FAILED_RESPONSE = {"status": STATUS_ERROR}



@router.post("/extraction_api")
async def extraction(payload: ProcessTask, background_task: BackgroundTasks):
  """extracts the document with given case id and uid
        Args:
             payload (ProcessTask): Consist of configs required to run the pipeline
                    uid (str): unique id for  each document
                    doc_class (str): class of document (processor is configured per document class)
        Returns:
            200 : PDF files are successfully classified and database updated
            500  : HTTPException: 500 Internal Server Error if something fails
            404 : Parser not available for given document
            :param background_task:
      """
  try:
    success_response = {"status": STATUS_SUCCESS}
    payload = payload.dict()
    Logger.info(f"extraction_api - payload received {payload}")
    configs = payload.get("configs")
    doc_class = payload.get("doc_class")
    Logger.info(f"extraction_api - Starting extraction for configs={configs},"
                f"doc_class={doc_class}")

    doc_configs = []
    for config in configs:
      uid = config.get("uid")
      document = Document.find_by_uid(uid)
      if not document:
        Logger.error(f"extraction_api - Could not retrieve document by uid {uid}")
        continue

      case_id = document.case_id
      gcs_url = document.url
      context = document.context
      document_type = document.document_type
      doc_configs.append(DocumentWrapper(case_id=case_id,
                                        uid=uid,
                                        gcs_url=gcs_url,
                                        document_type=document_type,
                                        context=context,
                                        ))

    background_task.add_task(extract_entities,
                             doc_configs,
                             doc_class)

    Logger.info(f"extraction - returning response")
    return success_response

  except Exception as e:
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(f"extraction_api - Extraction failed")
    Logger.error(e)
    Logger.error(err)
    raise HTTPException(status_code=500)


