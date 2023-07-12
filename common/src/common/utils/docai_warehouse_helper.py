"""
Copyright 2023 Google LLC

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
from typing import List

"""
Document Warehouse APi calls
"""

from .document_warehouse_utils import DocumentWarehouseUtils
from common.utils.logging_handler import Logger


def process_document(project_number: str,
                     api_location: str,
                     folder_id: str,
                     display_name: str,
                     document_schema_id: str,
                     caller_user: str,
                     bucket_name: str, document_path: str,
                     document_ai_output):
  try:
    Logger.info(f"process_document with project_number={project_number}, "
                f"api_location={api_location}, folder_id={folder_id}, "
                f"display_name={display_name}, document_schema_id="
                f"{document_schema_id}, caller_user={caller_user}, "
                f"bucket_name={bucket_name}, document_path={document_path}")
    dw_utils = DocumentWarehouseUtils(project_number=project_number,
                                      api_location=api_location)

    create_document_response = dw_utils.create_document(
        display_name=display_name,
        mime_type="application/pdf",
        document_schema_id=document_schema_id,
        raw_document_path=f"gs://{bucket_name}/{document_path}",
        docai_document=document_ai_output,
        caller_user_id=caller_user)

    Logger.info(f"process_document create_document_response"
                f"={create_document_response}")
    document_id = create_document_response.document.name.split("/")[-1]

    # TODO how to link one document to multiple folders
    link_document_response = dw_utils.link_document_to_folder(
        document_id=document_id,
        folder_document_id=folder_id,
        caller_user_id=caller_user)
    Logger.info(f"process_document link_document_response"
                f"={link_document_response}")
  except Exception as e:
    Logger.error(
        f"process_document - Error for {document_path}:  {e}")
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
