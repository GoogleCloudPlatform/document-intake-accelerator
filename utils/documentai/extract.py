import argparse
import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__),
                             '../../microservices/extraction_service/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/src'))

from utils import extract_entities
from common.utils import helper
from common.utils.format_data_for_bq import format_data_for_bq
from common.config import DocumentWrapper

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
  args_parser.add_argument('-c', dest="doc_class",
                           help="name of the document class",
                           default="generic_form")

  return args_parser


from google.cloud import storage

storage_client = storage.Client()


# python utils/extract.py -f gs://prior-auth-poc-pa-forms/demo/form.pdf -c claims_form
# python utils/extract.py -f gs://$PROJECT_ID-pa-forms/demo/pa-form-1.pdf -c prior_auth_form

# Process Directory
# python utils/extract.py -d gs://$PROJECT_ID/sample_data/pa-forms -c prior_auth_form


def process_dir(dir_uri):
  bucket_name, prefix = helper.split_uri_2_bucket_prefix(dir_uri)
  blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
  file_uris = [f"gs://{bucket_name}/{blob.name}" for blob in blobs]
  process(file_uris)


def process_file(file_uri, doc_class):
  print(f"file_uri={file_uri} doc_class={doc_class}")
  bucket_name, name = helper.split_uri_2_bucket_prefix(file_uri)
  bucket = storage_client.bucket(bucket_name)
  stats = storage.Blob(bucket=bucket, name=name).exists(storage_client)

  if not stats:
    print(f"ERROR: File URI {file_uri} does not exist on GCP CLoud Storage")
  else:
    process([file_uri])


def process(file_uris):
  context = "california"
  # extract_enitities.extract(file_uri, args.doc_class, context)

  configs = []
  for uri in file_uris:
    case_id = str(uuid.uuid1())
    uid = str(uuid.uuid1())
    gcs_url = uri
    document_type = "supporting_documents"
    configs.append(DocumentWrapper(case_id=case_id,
                                   uid=uid,
                                   gcs_url=gcs_url,
                                   document_type=document_type,
                                   context=context,
                                   ))
  extraction_output = extract_entities.extract_entities(configs, doc_class)
  for conf in extraction_output:
    entities_fo_bq = extraction_output[conf][0]
    formated_data = format_data_for_bq(entities_fo_bq)
    print(formated_data)
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

  if not file_uri and not dir_uri:
    parser.print_help()
    exit()

  if file_uri:
    process_file(file_uri, doc_class)

  if dir_uri:
    process_dir(dir_uri, doc_class)
