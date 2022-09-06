"""
Config module to setup common environment
"""

import os, json


def load_config(filename):
  json_file = open(os.path.join(os.path.dirname(__file__), ".", filename))
  return json.load(json_file)


# ========= Overall =============================
PROJECT_ID = os.environ.get("PROJECT_ID", "")
if PROJECT_ID != "":
  os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
assert PROJECT_ID, "Env var PROJECT_ID is not set."

REGOIN = "us-central1"
PROCESS_TIMEOUT_SECONDS = 600

#List of application forms and supporting documents
APPLICATION_FORMS = ["unemployment_form"]
SUPPORTING_DOCS = ["driver_license", "claims_form", "utility_bill", "pay_stub"]

# Doc approval status, will reflect on the Frontend app.
STATUS_APPROVED = "Approved"
STATUS_REVIEW = "Need Review"
STATUS_REJECTED = "Rejected"
STATUS_PENDING = "Pending"
STATUS_IN_PROGRESS = "Processing"

STATUS_SUCCESS = "Complete"
STATUS_ERROR = "Error"
STATUS_TIMEOUT = "Timeout"

# ========= Document upload ======================
BUCKET_NAME = f"{PROJECT_ID}-document-upload"
TOPIC_ID = "queue-topic"
PROCESS_TASK_API_PATH = "/upload_service/v1/process_task"

# ========= Validation ===========================
BUCKET_NAME_VALIDATION = PROJECT_ID
PATH = f"gs://{PROJECT_ID}/Validation/rules.json"
PATH_TEMPLATE = f"gs://{PROJECT_ID}/Validation/templates.json"
BIGQUERY_DB = "validation.validation_table"
VALIDATION_TABLE = f"{PROJECT_ID}.validation.validation_table"

# ========= Classification =======================
# Endpoint Id where model is deployed.
# TODO: Please update this to your deployed VertexAI model ID.
VERTEX_AI_CONFIG = load_config("vertex_ai_config.json")
assert VERTEX_AI_CONFIG, "Unable to locate 'vertex_ai_config.json'"

CLASSIFICATION_ENDPOINT_ID = VERTEX_AI_CONFIG["endpoint_id"]
assert CLASSIFICATION_ENDPOINT_ID, "CLASSIFICATION_ENDPOINT_ID is not defined."

#Prediction Confidence threshold for the classifier to reject any prediction
#less than the threshold value.
CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.85

# Map to standardise predicted document class from classifier to
# standard document_class values
DOC_CLASS_STANDARDISATION_MAP = {
    "UE": "unemployment_form",
    "DL": "driver_license",
    "Claim": "claims_form",
    "Utility": "utility_bill",
    "PayStub": "pay_stub"
}

# ========= DocAI Parsers =======================

# To add parsers, edit /terraform/enviroments/dev/main.tf

PARSER_CONFIG = load_config("parser_config.json")
assert PARSER_CONFIG, "Unable to locate 'parser_config.json'"

# ========= HITL and Frontend UI =======================

# List of database keys and extracted entities that are searchable
DB_KEYS = [
    "active",
    "auto_approval",
    "is_autoapproved",
    "matching_score",
    "case_id",
    "uid",
    "url",
    "context",
    "document_class",
    "document_type",
    "upload_timestamp",
    "extraction_score",
    "is_hitl_classified",
]
ENTITY_KEYS = [
    "name",
    "dob",
    "residential_address",
    "email",
    "phone_no",
]

### Misc

# Used by E2E testing. Leave as blank by default.
DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "")
