import requests
import traceback
from endpoint_proxy import get_baseurl
from common.models.document import Document
from setup_e2e import create_table
from common.db_client import bq_client
from google.cloud import bigquery
from common.config import PROJECT_ID,DATABASE_PREFIX
BUCKET_NAME = "gs://document-upload-test"

def test_create_tabel():
  # Construct a BigQuery client object.
  client = bq_client()
  BIGQUERY_DB = "entities"
  # TODO(developer): Set dataset_id to the ID of the dataset to create.
  # dataset_id = "{}.your_dataset".format(client.project)
  dataset_id = f"{PROJECT_ID}.{DATABASE_PREFIX}"
  # Construct a full Dataset object to send to the API.
  dataset = bigquery.Dataset(dataset_id)

  # TODO(developer): Specify the geographic location where the dataset should reside.
  dataset.location = "US"

  # Send the dataset to the API for creation, with an explicit timeout.
  # Raises google.api_core.exceptions.Conflict if the Dataset already
  # exists within the project.
  dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
  print("Created dataset {}.{}".format(client.project, dataset.dataset_id))
  table_id = f"{PROJECT_ID}.{DATABASE_PREFIX}.{BIGQUERY_DB}"
  schema = [
  bigquery.SchemaField("document_class", "STRING", mode="NULLABLE"),
  bigquery.SchemaField("case_id", "STRING", mode="NULLABLE"),
  bigquery.SchemaField("uid", "STRING", mode="NULLABLE"),
  bigquery.SchemaField("document_type", "STRING", mode="NULLABLE"),
  bigquery.SchemaField("entities", "STRING", mode="NULLABLE")

]

  table = bigquery.Table(table_id, schema=schema)
  table = client.create_table(table)  # Make an API request.
  print(
      "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
  )

def test_uuj_5():
  """
    UUJ 5 - Process the uploaded application form
    1. Classify the document
    2. Perform extraction on the classified document
    3. Autoapprove
  """
  
  case_id = "test123_x2"
  uid="tI03AfAUpwZECYd5f6OM"
  file = "Copy of Arkansas-form-1.pdf"
  gcs_url = f"{BUCKET_NAME}/{case_id}/{uid}/{file}"
  d = Document()
  d.uid = uid
  d.case_id = case_id
  d.context = "arkansas"
  d.url = gcs_url
  d.save()
#   Run classification
  classification_url = get_baseurl("classification-service")
  response = requests.post(classification_url+f"/classification_service/v1/classification/classification_api?case_id={case_id}&uid={uid}&gcs_url={gcs_url}")
  assert response.status_code == 200
  print("==================classification successful in uuj5===================")
#   Run extraction for the document
  d.document_class = "unemployment_form"
  d.document_type = "application_form"
  d.save()
  extraction_url = get_baseurl("extraction-service")
  response = requests.post(extraction_url+f"/extraction_service/v1/extraction_api?case_id={case_id}&uid={uid}&doc_class=unemployment_form&document_type=application_form&context=arkansas&gcs_url={gcs_url}")
  assert response.status_code == 200
  print("==================extraction successful in uuj5===================")
#  Run autoapproval
  dsu_url = get_baseurl("document-status-service")
  response = requests.post(dsu_url+f"/document_status_service/v1/update_autoapproved_status?case_id={case_id}&uid={uid}&status=success&autoapproved_status=Approved&is_autoapproved=yes")
  assert response.status_code == 200
  print("==================autoapproval successful in uuj5===================")
  