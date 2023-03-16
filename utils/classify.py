import argparse
import os

import sys

sys.path.append(os.path.join(os.path.dirname(__file__),
                             '../microservices/classification_service/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../common/src'))

from routes import classification
from common.utils import helper
from google.cloud import storage
from common.config import get_document_type

# python utils/extract.py -f gs://
# Make sure to SET GOOGLE_APPLICATION_CREDENTIALS
# export DEBUG=true
# Make sure to source SET
# Make sure to pass remote URL

# gcloud auth activate-service-account [ACCOUNT] --key-file=KEY_FILE
# gcloud auth activate-service-account development@ek-cda-engine.iam.gserviceaccount.com --key-file=/Users/evekhm/ek-cda-engine-1e2875b4e6ec.json
# gcloud iam service-accounts create local-dev --description="local development" --display-name="local dev"

# gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:local-dev@$PROJECT_ID.iam.gserviceaccount.com"
#         --role="roles/storage.admin"
# gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:local-dev@$PROJECT_ID.iam.gserviceaccount.com" \
#         --role="roles/logging.admin"

# gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:local-dev@$PROJECT_ID.iam.gserviceaccount.com" \
#         --role="roles/documentai.admin"


# gcloud iam service-accounts keys create ~/local_dev.json \
#     --iam-account=local-dev@$PROJECT_ID.iam.gserviceaccount.com

PROJECT_ID = os.environ.get("PROJECT_ID", "")
print(f"PROJECT_ID={PROJECT_ID}")
print(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""))
os.environ[
  "PARSER_CONFIG_FILE"] = f"gs://{PROJECT_ID}/config/parser_config_demo.json"
# os.environ["PARSER_CONFIG_FILE"] = os.path.join(os.path.dirname(__file__), '../common/src/common/parser_config_demo.json')
os.environ[
  "DOCAI_ENTITY_MAPPING_FILE"] = f"gs://{PROJECT_ID}/config/docai_entity_mapping.json"
# os.environ["DOCAI_ENTITY_MAPPING_FILE"] = os.path.join(os.path.dirname(__file__), '../common/src/common/docai_entity_mapping.json')
os.environ["DEBUG"] = 'True'


def get_parser():
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




storage_client = storage.Client()


# python utils/extract.py -f gs://prior-auth-poc-pa-forms/demo/form.pdf
# python utils/extract.py -f gs://$PROJECT_ID-pa-forms/demo/pa-form-1.pdf
# Process Directory
# python utils/extract.py -d gs://$PROJECT_ID/sample_data/pa-forms


def process_dir(dir_uri):
  bucket_name, prefix = helper.split_uri_2_bucket_prefix(dir_uri)
  blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
  for blob in blobs:
    print(f"Processing {blob.name}")
    process_file(f"gs://{bucket_name}/{blob.nane}")


def process_file(file_uri):
  bucket_name, name = helper.split_uri_2_bucket_prefix(file_uri)
  bucket = storage_client.bucket(bucket_name)
  stats = storage.Blob(bucket=bucket, name=name).exists(storage_client)

  if not stats:
    print(f"ERROR: File URI {file_uri} does not exist on GCP CLoud Storage")
  else:

    classification_output = classification.predict_doc_type("case_id", "uid",
                                                            file_uri)
    print(classification_output)
    doc_class = classification_output["predicted_class"]
    doc_type = get_document_type(doc_class)
    classification_score = classification_output["model_conf"]
    print(f"Classification confidence  gcs_url={file_uri} is {classification_score},"
                f" doc_type={doc_type}, doc_class={doc_class} ")


if __name__ == "__main__":
  parser = get_parser()
  args = parser.parse_args()

  file_uri = args.file_uri
  dir_uri = args.dir_uri

  if not file_uri and not dir_uri:
    parser.print_help()
    exit()

  if file_uri:
    process_file(file_uri)

  if dir_uri:
    process_dir(dir_uri)
