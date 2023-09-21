import argparse
import os
import sys

from google.cloud import storage

sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/src'))
from common.utils.document_warehouse_utils import DocumentWarehouseUtils
from common.utils.document_ai_utils import DocumentaiUtils
from load_docs import create_document_schema

storage_client = storage.Client()

API_LOCATION = "us"  # Choose "us" or "eu"
DOCAI_WH_PROJECT_NUMBER = os.environ[
  "DOCAI_WH_PROJECT_NUMBER"]  # Set this to your DW project number
CALLER_USER = f"user:{os.environ['CALLER_USER']}"  # service account
PROCESSOR_ID = os.environ.get("PROCESSOR_ID")  # Processor ID inside DW project
GCS_OUTPUT_BUCKET = os.environ.get(
    "DOCAI_OUTPUT_BUCKET")  # GCS Folder to be used for the DocAI output
DOCAI_PROJECT_NUMBER = os.environ.get(
    "DOCAI_PROJECT_NUMBER")  # GCS Folder to be used for the DocAI output

folder_schema_path = os.path.join(os.path.dirname(__file__),
                                  "schema_files/folder_schema.json")
document_schema_path = os.path.join(os.path.dirname(__file__),
                                    "./schema_files/document_schema.json")

assert DOCAI_WH_PROJECT_NUMBER, "DOCAI_WH_PROJECT_NUMBER not set"
assert DOCAI_PROJECT_NUMBER, "DOCAI_PROJECT_NUMBER not set"
assert PROCESSOR_ID, "PROCESSOR_ID not set"
assert GCS_OUTPUT_BUCKET, "DOCAI_OUTPUT_BUCKET not set"

dw_utils = DocumentWarehouseUtils(project_number=DOCAI_WH_PROJECT_NUMBER,
                                  api_location=API_LOCATION)
docai_utils = DocumentaiUtils(project_number=DOCAI_PROJECT_NUMBER,
                              api_location=API_LOCATION)


def get_args():
  # Read command line arguments
  args_parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      Script to generate draft DocaiWH document schema using Docai output.
      """,
      epilog="""
      Examples:

      python upload_schema.py -f=gs://my-folder/parser_name.json [-o]]
      """)

  args_parser.add_argument('-f', dest="schema_path",
                           help="Path to document schema json file.", required=True)
  args_parser.add_argument('-o', '--overwrite', dest="overwrite",
                           help="Overwrite files if already exist.",
                           action='store_true', default=False)
  return args_parser


def main():
  create_document_schema(schema_path, overwrite)


if __name__ == "__main__":
  parser = get_args()
  args = parser.parse_args()
  schema_path = args.schema_path
  overwrite = args.overwrite
  main()
