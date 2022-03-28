"""
Config module to setup common environment
"""

import os

PROJECT_ID = os.environ.get("PROJECT_ID", "")

if PROJECT_ID != "":
  os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID

DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "")


BUCKET_NAME ="document-upload-test"
PATH ="gs://async_form_parser/Jsons/trial.json"
PROJECT_ID ="claims-processing-dev"

