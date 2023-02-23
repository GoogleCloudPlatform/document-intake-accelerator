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

""" Process task api endpoint """
from fastapi import APIRouter, HTTPException
import traceback
from common.utils.logging_handler import Logger
from common.config import get_config
from common.config import STATUS_SUCCESS, STATUS_ERROR

router = APIRouter()
SUCCESS_RESPONSE = {"status": STATUS_SUCCESS}
FAILED_RESPONSE = {"status": STATUS_ERROR}


@router.get("/get_config")
async def get_config_by_name(name=None):
  """ reports document_types_config
          Returns:
              200 : fetches all the data from database
              500 : If any error occurs
    """

  try:
    # Fetching only active documents
    Logger.info(f"get_config called for {name}")
    config = get_config(name)
    Logger.info(f"get_config config={config}")
    response = SUCCESS_RESPONSE
    response["data"] = config
    return response

  except Exception as e:
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500, detail="Error in get_document_types_config") from e

