import argparse
import os
import sys

from docai_helper import get_upload_file_path

sys.path.append(os.path.join(os.path.dirname(__file__),
                             '../../microservices/extraction_service/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/src'))

from utils import extract_entities
from common.utils import helper
import common.config
from common.utils.logging_handler import Logger
from common.utils.helper import get_processor_location
import asyncio
from google.cloud import documentai_v1 as documentai

from google.cloud import storage


storage_client = storage.Client()
# python utils/extract.py -f gs://
# Make sure to SET GOOGLE_APPLICATION_CREDENTIALS
# export DEBUG=true
# Make sure to source SET
# Make sure to pass remote URL

# gcloud auth activate-service-account [ACCOUNT] --key-file=KEY_FILE
# gcloud auth activate-service-account development@ek-cda-engine.iam.gserviceaccount.com --key-file=/Users/evekhm/ek-cda-engine-1e2875b4e6ec.json
# gcloud iam service-accounts create local-dev --description="local development" --display-name="local dev"
# export GOOGLE_APPLICATION_CREDENTIALS
# gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:local-dev@$PROJECT_ID.iam.gserviceaccount.com"
#         --role="roles/storage.admin"
# gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:local-dev@$PROJECT_ID.iam.gserviceaccount.com" \
#         --role="roles/logging.admin"

# gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:local-dev@$PROJECT_ID.iam.gserviceaccount.com" \
#         --role="roles/documentai.admin"

# gcloud auth login
# gcloud auth application-default login

# gcloud iam service-accounts keys create ~/local_dev.json \
#     --iam-account=local-dev@$PROJECT_ID.iam.gserviceaccount.com

PROJECT_ID = os.environ.get("PROJECT_ID", "")
print(f"PROJECT_ID={PROJECT_ID}")
print(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""))
os.environ["CONFIG_FILE"] = f"gs://{PROJECT_ID}-config/config.json"
os.environ["DEBUG"] = 'True'


def get_args():
  # Read command line arguments
  args_parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      script to Test Document AI Extraction.
      """,
      epilog="""
      Examples:

      python generate_images.py -f=gs-path-to-form.pdf -d=gs-path-to-dir [-c=doc_class]]
      """)

  args_parser.add_argument('-d', dest="dir_uri",
                           help="Path to gs directory uri")
  args_parser.add_argument('-f', dest="file_uri", help="Path to gs uri")
  args_parser.add_argument('-p', dest="parser_name",
                           help="name of the parser as specified in the config.json",
                           default="claims_form_parser")
  args_parser.add_argument('-c', dest="doc_class",
                           help="name of the document class")
  return args_parser


# python utils/extract.py -f gs://prior-auth-poc-pa-forms/demo/form.pdf -c claims_form
# python utils/extract.py -f gs://$PROJECT_ID-pa-forms/demo/pa-form-1.pdf -c prior_auth_form

# Process Directory
# python utils/extract.py -d gs://$PROJECT_ID/sample_data/pa-forms -c prior_auth_form


async def process_dir():
  bucket_name, prefix = helper.split_uri_2_bucket_prefix(dir_uri)
  blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
  file_uris = [f"gs://{bucket_name}/{blob.name}" for blob in blobs]
  upload_uris = []
  for uri in file_uris:
    uid, path = get_upload_file_path(uri, doc_class=doc_class)
    upload_uris.append(path)
    uids.append(uid)

  await process(upload_uris)


async def process_file():
  print(f"file_uri={file_uri} parser_name={parser_name}")
  bucket_name, name = helper.split_uri_2_bucket_prefix(file_uri)
  bucket = storage_client.bucket(bucket_name)
  stats = storage.Blob(bucket=bucket, name=name).exists(storage_client)

  if not stats:
    print(f"ERROR: File URI {file_uri} does not exist on GCP CLoud Storage")
  else:
    uid, file_uri_upload = get_upload_file_path(file_uri, doc_class=doc_class)
    uids.append(uid)
    await process([file_uri_upload])


async def start(processor, dai_client, input_uris):
  await extract_entities.batch_extraction(processor, dai_client, input_uris)


async def process(input_uris):
  parser_details = common.config.get_parser_by_name(parser_name)

  if not parser_details:
    Logger.error(f"extraction_api - Parser {parser_name} not defined in config")
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

  await extract_entities.batch_extraction(processor, dai_client, input_uris)
  # extraction_output = extract_entities.extract_entities(configs, doc_class)
  # for item in extraction_output:
  #   entities_fo_bq = item.extracted_entities
  #   formated_data = format_data_for_bq(entities_fo_bq)
  #   print(formated_data)
  # is_tuple = isinstance(extraction_output, tuple)
  #
  # if is_tuple and isinstance(extraction_output[0], list):
  #   # call the format_data_bq function to format data to be
  #   # inserted in Bigquery
  #   for uri
  #   entities_for_bq = format_data_for_bq(extraction_output[0])


if __name__ == "__main__":
  parser = get_args()
  args = parser.parse_args()

  file_uri = args.file_uri
  dir_uri = args.dir_uri
  doc_class = args.doc_class
  parser_name = args.parser_name
  if doc_class:
    parser_name = common.config.get_parser_name_by_doc_class(doc_class)

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
    # uids_str = ",".join(uids)
    # for uid in uids:
    #   print(f"Cleaning up following uid from Firestore {uid}")
    #   models.Document.delete_by_id(uid)
    loop.close()
