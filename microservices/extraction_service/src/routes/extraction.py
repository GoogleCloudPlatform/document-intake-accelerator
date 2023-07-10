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

""" extraction endpoints """
import traceback

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import HTTPException
from models.process_task import ProcessTask
from utils.extract_entities import extract_entities

from common.config import STATUS_ERROR
from common.config import STATUS_SUCCESS
from common.utils.docai_helper import get_docai_input
from common.utils.logging_handler import Logger

# disabling for linting to pass
# pylint: disable = broad-except
router = APIRouter()

FAILED_RESPONSE = {"status": STATUS_ERROR}
SUCCESS_RESPONSE = {"status": STATUS_SUCCESS}


@router.post("/extraction_api")
async def extraction(payload: ProcessTask, background_task: BackgroundTasks):
  """extracts the document with given case id and uid
        Args:
             payload (ProcessTask): Consist of configs required to run the pipeline
                    uid (str): unique id for  each document
                    parser_name (str): name of the parser (as in config.json) to be used for the extraction
        Returns:
            200 : PDF files are successfully classified and database updated
            500  : HTTPException: 500 Internal Server Error if something fails
            404 : Parser not available for given document
            :param background_task:
      """
  try:
    payload = payload.dict()
    Logger.info(f"extraction_api - payload received {payload}")
    configs = payload.get("configs")
    parser_name = payload.get("parser_name")
    Logger.info(f"extraction_api - Starting extraction for configs={configs}, parser_name={parser_name}")

    processor, dai_client, input_uris = get_docai_input(parser_name, configs)
    if not processor or not dai_client:
      Logger.error(f"extraction_api - Failed to get processor {parser_name} using config")
      return FAILED_RESPONSE

    if not dai_client:
      Logger.error(f"extraction_api - Unidentified location for parser {parser_name}")
      return FAILED_RESPONSE

    background_task.add_task(extract_entities,
                             processor, dai_client, input_uris)

    Logger.info(f"extraction_api - returning response")
    return SUCCESS_RESPONSE

  except Exception as e:
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(f"extraction_api - Extraction failed")
    Logger.error(e)
    Logger.error(err)
    raise HTTPException(status_code=500)
