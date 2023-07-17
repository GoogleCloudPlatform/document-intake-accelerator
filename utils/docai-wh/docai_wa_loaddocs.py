import argparse
import json
import os
import sys

from google.cloud import storage
import time
from google.api_core.exceptions import NotFound

sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/src'))
from common.utils.logging_handler import Logger
from common.utils.document_warehouse_utils import DocumentWarehouseUtils
from common.utils.document_ai_utils import DocumentaiUtils
from common.utils import storage_utils, helper

API_LOCATION = "us"  # Choose "us" or "eu"
DOCAI_WH_PROJECT_NUMBER = os.environ["DOCAI_WH_PROJECT_NUMBER"]  # Set this to your DW project number
caller_user = f"user:{os.environ['CALLER_USER']}"  # service account
PROCESSOR_ID = os.environ.get("PROCESSOR_ID")     # Processor ID inside DW project
GCS_OUTPUT_BUCKET = os.environ.get("DOCAI_OUTPUT_BUCKET")  # GCS Folder to be used for the DocAI output
DOCAI_PROJECT_NUMBER = os.environ.get("DOCAI_PROJECT_NUMBER")  # GCS Folder to be used for the DocAI output

folder_schema_path = "./schema_files/folder_schema.json"
document_schema_path = "./schema_files/document_schema.json"

assert DOCAI_WH_PROJECT_NUMBER, "DOCAI_WH_PROJECT_NUMBER not set"
assert DOCAI_PROJECT_NUMBER, "DOCAI_PROJECT_NUMBER not set"
assert caller_user, "CALLER_USER not set"
assert PROCESSOR_ID, "PROCESSOR_ID not set"
assert GCS_OUTPUT_BUCKET, "DOCAI_OUTPUT_BUCKET not set"

dw_utils = DocumentWarehouseUtils(project_number=DOCAI_WH_PROJECT_NUMBER,
                                  api_location=API_LOCATION)
docai_utils = DocumentaiUtils(project_number=DOCAI_PROJECT_NUMBER,
                              api_location=API_LOCATION)

storage_client = storage.Client()
schema_id_list = []
document_id_list = []
created_folders = []
files_to_parse = {}
processed_files = []
processed_dirs = set()
error_files = []


def main(dir_uri, root_name):
  initial_start_time = time.time()

  folder_schema_id = create_folder_schema(folder_schema_path)
  document_schema_id = create_document_schema(document_schema_path)

  bucket_name, prefix = helper.split_uri_2_bucket_prefix(dir_uri)
  blobs = storage_client.list_blobs(bucket_name, prefix=prefix)

  if root_name is None: root_name = bucket_name

  for blob in blobs:
    filename = blob.name

    Logger.info(f'Handling {filename}')

    try:
      if filename.endswith(".pdf"):
        dirs = filename.split("/")

        parent_id = create_folder(folder_schema_id, root_name, root_name)
        parent = dw_utils.get_document(parent_id, caller_user)

        for d in dirs:
          reference_id = f"{parent.reference_id}__{d}".strip()
          if not d.endswith(".pdf"):
            processed_dirs.add(d)
            if reference_id not in created_folders:
              sub_folder_id = create_folder(folder_schema_id, d, reference_id)
              dw_utils.create_folder_link_document(
                  f"{dw_utils.location_path()}/documents/{parent_id}",
                  f"{dw_utils.location_path()}/documents/{sub_folder_id}",
                  caller_user)
              created_folders.append(reference_id)

            parent = dw_utils.get_document(f"referenceId/{reference_id}", caller_user)
            parent_id = parent.name.split("/")[-1]
          else:
            if document_exists(reference_id):
              Logger.info(f"Skipping gs://{bucket_name}/{filename} since it already exists...")
            else:
              files_to_parse[f"gs://{bucket_name}/{filename}"] = (document_schema_id, parent_id, reference_id)

            processed_files.append(filename)
    except Exception as ex:
      Logger.error(f"Exception {ex} while handling {filename}")
      error_files.append(filename)

  # Process All Documents in One batch
  docai_output_list = docai_utils.batch_extraction(PROCESSOR_ID, list(files_to_parse.keys()), GCS_OUTPUT_BUCKET)
  for f_uri in docai_output_list:
    document_ai_output = docai_output_list[f_uri]
    if f_uri in files_to_parse:
      (document_schema_id, parent_id, reference_id) = files_to_parse[f_uri]
      upload_document_gcs(f_uri, document_schema_id, parent_id, reference_id, document_ai_output)

  process_time = time.time() - initial_start_time
  time_elapsed = round(process_time)
  Logger.info(f"Job Completed in {str(round(time_elapsed/60))} minutes: \n"
        f"  - processed_files={len(processed_files)} \n"
        f"  - created_documents={len(document_id_list)} \n"
        f"  - processed_directories={len(processed_dirs)} \n"
        f"  - created_directories={len(created_folders)} \n")

  if len(error_files) != 0:
    Logger.info(f"Following files could not be handled (Document page number exceeding limit of 15 pages?")
    ",".join(error_files)


def document_exists(reference_id: str) -> bool:
  reference_path = f"referenceId/{reference_id}"
  try:
    dw_utils.get_document(reference_path, caller_user)
    return True
  except NotFound as e:
    return False


def upload_document_gcs(file_uri: str, document_schema_id: str,
                        folder_id: str, reference_id: str, document_ai_output):

    create_document_response = dw_utils.create_document(
        display_name=os.path.basename(file_uri),
        mime_type="application/pdf",
        document_schema_id=document_schema_id,
        raw_document_path=file_uri,
        docai_document=document_ai_output,
        caller_user_id=caller_user,
        reference_id=reference_id
    )

    Logger.debug(
        f"create_document_response={create_document_response}")  # Verify that the properties have been set correctly

    document_id = create_document_response.document.name.split("/")[-1]
    document_id_list.append(document_id)
    Logger.info(f"Created document {file_uri} with reference_id={reference_id}")

    dw_utils.link_document_to_folder(document_id=document_id,
                                     folder_document_id=folder_id,
                                     caller_user_id=caller_user)
    return document_id


def create_folder_schema(schema_path: str):
  folder_schema = storage_utils.read_file(schema_path, mode="r")
  display_name = json.loads(folder_schema).get("display_name")
  for ds in dw_utils.list_document_schemas():
    if ds.display_name == display_name and ds.document_is_folder:
      return ds.name.split("/")[-1]

  create_schema_response = dw_utils.create_document_schema(folder_schema)
  folder_schema_id = create_schema_response.name.split("/")[-1]

  Logger.info(f"folder_schema_id={folder_schema_id}")
  response = dw_utils.get_document_schema(schema_id=folder_schema_id)
  Logger.debug(f"response={response}")
  return folder_schema_id


def create_folder(folder_schema_id: str, display_name: str, reference_id: str) \
    -> str:
  reference_path = f"referenceId/{reference_id}"
  try:
    document = dw_utils.get_document(reference_path, caller_user)
    folder_id = document.name.split("/")[-1]
  except NotFound as e:
    Logger.info(
        f" -------> Creating sub-folder [{display_name}] with reference_id=[{reference_id}]")
    create_folder_response = dw_utils.create_document(display_name=display_name,
                                                      document_schema_id=folder_schema_id,
                                                      caller_user_id=caller_user,
                                                      reference_id=reference_id)
    folder_id = create_folder_response.document.name.split("/")[-1]
  return folder_id


def create_document_schema(schema_path: str):
  document_schema = storage_utils.read_file(schema_path, mode="r")
  display_name = json.loads(document_schema).get("display_name")
  for ds in dw_utils.list_document_schemas():
    if ds.display_name == display_name and not ds.document_is_folder:
      return ds.name.split("/")[-1]

  create_schema_response = dw_utils.create_document_schema(document_schema)
  document_schema_id = create_schema_response.name.split("/")[-1]
  return document_schema_id


def get_args():
  # Read command line arguments
  args_parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      script to Batch load PDF data into the Document AI Warehouse.
      """,
      epilog="""
      Examples:

      python docai_wa_loaddocs.py -d=gs://my-folder [-n=UM_Guidelines]]
      """)

  args_parser.add_argument('-d', dest="dir_uri",
                           help="Path to gs directory uri, containing data with PDF documents to be loaded. All original structure of sub-folders will be preserved.")
  args_parser.add_argument('-n', dest="root_name",
                           help="Name of the root folder inside DW where "
                                "documents will be loaded. When skipped, will use the same name of the folder being loaded from.")
  return args_parser


if __name__ == "__main__":
  parser = get_args()
  args = parser.parse_args()

  dir_uri = args.dir_uri
  root_name = args.root_name
  main(dir_uri, root_name)
