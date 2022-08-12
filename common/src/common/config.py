"""
Config module to setup common environment
"""

import os

PROJECT_ID = os.environ.get("PROJECT_ID", "")

if PROJECT_ID != "":
  os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID

DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "")
BUCKET_NAME = f"{PROJECT_ID}-document-upload"
BUCKET_NAME_VALIDATION = PROJECT_ID
PATH = f"gs://{PROJECT_ID}/Validation/rules.json"
PATH_TEMPLATE = f"gs://{PROJECT_ID}/Validation/templates.json"
BIGQUERY_DB = "validation.validation_table"
TOPIC_ID = "queue-topic"
VALIDATION_TABLE = f"{PROJECT_ID}.validation.validation_table"

# Endpoint Id where model is deployed.
# TODO: Please update this to your deployed VertexAI model ID.
ENDPOINT_ID = "4679565468279767040"

#Map to standardise predicted document class from classifier to
# standard document_class values
DOC_CLASS_STANDARDISATION_MAP = {
  "UE": "unemployment_form",
  "DL": "driving_licence",
  "Claim": "claims_form",
  "Utility": "utility_bill",
  "PayStub": "pay_stub"
}

#List of application forms and supporting documents
APPLICATION_FORMS = ["unemployment_form"]
SUPPORTING_DOCS = ["driving_licence","claims_form","utility_bill","pay_stub"]

#List of database keys and extracted entities that are searchable
DB_KEYS = [
    "active", "auto_approval", "is_autoapproved", "matching_score", "case_id",
    "uid", "url", "context", "document_class", "document_type",
    "upload_timestamp", "extraction_score", "is_hitl_classified"
]

ENTITY_KEYS = ["name", "dob", "residential_address", "email", "phone_no"]

# Classification Configs
#Prediction Confidence threshold for the classifier to reject any prediction
#less than the threshold value.
CONF_THRESH = 0.98

