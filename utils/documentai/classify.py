import argparse
import datetime
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),
                             '../../microservices/classification_service/src'))

sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/src'))
from docai_helper import get_upload_file_path
from common import models
from common.utils.logging_handler import Logger
from common.utils import helper
from google.cloud import storage
from common.config import CLASSIFIER
from common.utils.helper import get_processor_location
from utils.classification.split_and_classify import \
  batch_classification
from common.utils.helper import get_id_from_file_path

import asyncio
from google.cloud import documentai_v1 as documentai
import common.config
from common.docai_config import DOCAI_OUTPUT_BUCKET_NAME
# python utils/classify_test.py -f gs://
# Make sure to SET GOOGLE_APPLICATION_CREDENTIALS
# Make sure to source SET
# Make sure to pass remote URI

# gcloud auth activate-service-account [ACCOUNT] --key-file=KEY_FILE
# gcloud auth activate-service-account development@ek-cda-engine.iam.gserviceaccount.com --key-file=/Users/evekhm/ek-cda-engine-1e2875b4e6ec.json
# gcloud iam service-accounts create local-dev --description="local development" --display-name="local dev"

PROJECT_ID = os.environ.get("PROJECT_ID", "")
print(f"PROJECT_ID={PROJECT_ID}")
print(
    f'GOOGLE_APPLICATION_CREDENTIALS={os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")}')
print(f'CONFIG_BUCKET={os.environ.get("CONFIG_BUCKET")}')
PDF_MIME_TYPE = "application/pdf"

storage_client = storage.Client()
from common.models import Document


def get_args():
  # Read command line arguments
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      script to Test Document AI Classification.
      """,
      epilog="""
      Examples:

      python generate_images.py -f=gs-path-to-form.pdf -d=gs-path-to-dir [-c=doc_class]]
      """)

  parser.add_argument('-d', dest="dir_uri", help="Path to gs directory uri")
  parser.add_argument('-f', dest="file_uri", help="Path to gs uri")

  return parser


# python utils/extract.py -f gs://prior-auth-poc-pa-forms/demo/form.pdf
# python utils/extract.py -f gs://$PROJECT_ID-pa-forms/demo/pa-form-1.pdf
# Process Directory
# python utils/extract.py -d gs://$PROJECT_ID/sample_data/pa-forms
async def process(input_uris):
  parser_details = common.config.get_parser_by_name(CLASSIFIER)


  if not parser_details:
    Logger.error(f"extraction_api - Parser {CLASSIFIER} not defined in config")
    return

  processor_path = parser_details["processor_id"]
  location = parser_details.get("location",
                                get_processor_location(processor_path))
  if not location:
    Logger.error(
        f"extraction_api - Unidentified location for parser {processor_path}")
    return

  opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}

  dai_client = documentai.DocumentProcessorServiceClient(
      client_options=opts)
  processor = dai_client.get_processor(name=processor_path)

  await batch_classification(processor, dai_client, input_uris)


def get_callback_fn(operation):
  def post_process_extract(future):
    print(f"post_process_extract - Extraction Complete!")
    print(f"post_process_extract - operation.metadata={operation.metadata}")

    result = []
    print(f"post_process_extract {result}")

  return post_process_extract


async def process_dir():
  bucket_name, prefix = helper.split_uri_2_bucket_prefix(dir_uri)
  blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
  file_uris = [f"gs://{bucket_name}/{blob.name}" for blob in blobs]
  upload_uris = []
  for uri in file_uris:
    uid, path = get_upload_file_path(uri)
    upload_uris.append(get_upload_file_path(uri))
    uids.append(uid)
  await process(upload_uris)


async def process_file():
  bucket_name, name = helper.split_uri_2_bucket_prefix(file_uri)
  bucket = storage_client.bucket(bucket_name)
  stats = storage.Blob(bucket=bucket, name=name).exists(storage_client)

  if not stats:
    print(f"ERROR: File URI {file_uri} does not exist on GCP CLoud Storage")
  else:
    uid, file_uri_upload = get_upload_file_path(file_uri)
    uids.append(uid)
    await process([file_uri_upload])

    # doc_class = classification_output["predicted_class"]
    # doc_type = get_document_type(doc_class)
    # classification_score = classification_output["model_conf"]
    # print(
    #   f"Classification confidence  gcs_url={file_uri} is {classification_score},"
    #   f" doc_type={doc_type}, doc_class={doc_class} ")


if __name__ == "__main__":
  parser = get_args()
  args = parser.parse_args()

  file_uri = args.file_uri
  dir_uri = args.dir_uri

  if not file_uri and not dir_uri:
    parser.print_help()
    exit()

  loop = asyncio.get_event_loop()
  uids = []
  try:
    if file_uri:
      asyncio.ensure_future(process_file())

    if dir_uri:
      asyncio.ensure_future(process_dir())
    loop.run_forever()
  except KeyboardInterrupt:
    pass
  finally:
    uids_str = ",".join(uids)
    # for uid in uids:
      # print(f"Cleaning up following uid from Firestore {uid}")
      # models.Document.delete_by_id(uid)
    loop.close()
