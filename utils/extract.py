import argparse
import os

import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../microservices/extraction_service/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../common/src'))

from utils import extract_enitities

# python utils/extract.py -f sample_data/
# Make sure to SET GOOGLE_APPLICATION_CREDENTIALS

# gcloud auth activate-service-account [ACCOUNT] --key-file=KEY_FILE
# gcloud auth activate-service-account development@ek-cda-engine.iam.gserviceaccount.com --key-file=/Users/evekhm/ek-cda-engine-1e2875b4e6ec.json
#gcloud iam service-accounts create local-dev --description="local development" --display-name="local dev"

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
os.environ["PARSER_CONFIG_FILE"] = f"gs://{PROJECT_ID}/config/parser_config_demo.json"
#os.environ["PARSER_CONFIG_FILE"] = os.path.join(os.path.dirname(__file__), '../common/src/common/parser_config_demo.json')
os.environ["DOCAI_ENTITY_MAPPING_FILE"] = f"gs://{PROJECT_ID}/config/docai_entity_mapping.json"
#os.environ["DOCAI_ENTITY_MAPPING_FILE"] = os.path.join(os.path.dirname(__file__), '../common/src/common/docai_entity_mapping.json')
os.environ["DEBUG"] = 'True'

def get_parser():

  # Read command line arguments
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      script to Test Document AI Extraction.
      """,
      epilog="""
      Examples:

      python generate_images.py -f=path-to-form.pdf
      """)

  parser.add_argument('-f', dest="file", help="Path to gs uri", required=True,)
  parser.add_argument('-c', dest="doc_class", help="name of the document class", required=True,)

  return parser


parser = get_parser()
args = parser.parse_args()

# files_list = []
# print(args.files)
# print(args.dirs)
# for f in args.files:
#   if f.startswith("gs://"):
#     files_list.append(f)
#   else:
#     print(f"Is not a valid path to a file {f}")
#
# for d in args.dirs:
#   if os.path.isdir(d):
#     for file in os.listdir(d):
#       if file.endswith(".pdf"):
#         files_list.append(file)
#   else:
#     print(f"Is not a valid path to a directory {d}")
#
# print(",".join(files_list))

doc_class = "prior_auth_form"
doc_class = "claims_form"
context = "california"
extract_enitities.extract(args.file, args.doc_class, context)

#python utils/extract.py -f gs://prior-auth-poc-pa-forms/demo/form.pdf -c claims_form
# python utils/extract.py -f gs://$PROJECT_ID-pa-forms/demo/pa-form-1.pdf -c prior_auth_form
