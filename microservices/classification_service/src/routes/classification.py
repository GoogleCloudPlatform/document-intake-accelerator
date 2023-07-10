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

import traceback

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import HTTPException
from models.process_task import ProcessTask
from utils.classification.split_and_classify import batch_classification
from utils.classification.split_and_classify import update_classification_status

from common.config import CLASSIFIER
from common.config import STATUS_ERROR
from common.config import STATUS_SUCCESS
from common.config import get_classification_default_class
from common.utils.docai_helper import get_docai_input
from common.utils.helper import get_id_from_file_path
from common.utils.logging_handler import Logger

router = APIRouter(prefix="/classification")

FAILED_RESPONSE = {"status": STATUS_ERROR}
CLASSIFICATION_UNDETECTABLE = "unclassified"
SUCCESS_RESPONSE = {"status": STATUS_SUCCESS}


@router.post("/classification_api")
async def classification(payload: ProcessTask, background_task: BackgroundTasks):
  """classifies the  input and updates the active status of document in
        the database
      Args:
          payload (ProcessTask): Consist of configs required to run the pipeline
      Returns:
          200 : PDF files are successfully classified and database updated
          400 : Improper parameters
          422 : Document classified as invalid
          500 : Internal Server Error if something fails
    """
  try:

    payload = payload.dict()
    Logger.info(f"classification - payload received {payload}")
    configs = payload.get("configs")
    parser_name = CLASSIFIER
    Logger.info(
      f"classification - Starting extraction for configs={configs}, parser_name={parser_name}")

    Logger.info(f"classification_api starting classification for configs={configs}")
    # Making prediction
    processor, dai_client, input_uris = get_docai_input(parser_name, configs)

    # When classifier/splitter is not setup
    if not processor:
      # update status for all documents
      default_class = get_classification_default_class()
      Logger.warning(
        f"classification_api - No classification parser defined, exiting classification, "
        f"using {default_class}")
      for uri in input_uris:
        case_id, uid = get_id_from_file_path(uri)
        if uid is None:
          Logger.error(f"classification_api - Cannot find document with url = {uri}")
          continue

        #To refactor (one service waiting another one sync)
        update_classification_status(case_id,
                                     uid,
                                     STATUS_SUCCESS,
                                     document_class=default_class,
                                     classification_score=-1)
      return SUCCESS_RESPONSE

    background_task.add_task(batch_classification,
                             processor, dai_client, input_uris)
    Logger.info(f"classification_api  response: {SUCCESS_RESPONSE}")
    return SUCCESS_RESPONSE

  except Exception as e:
    Logger.error(f"{e} while classification ")
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    # DocumentStatus api call
    # update_classification_status(case_id, uid, STATUS_ERROR)
    raise HTTPException(status_code=500, detail=FAILED_RESPONSE) from e