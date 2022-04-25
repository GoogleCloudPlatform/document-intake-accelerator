from common.db_client import bq_client
from google.cloud import bigquery
from common.config import PROJECT_ID, DATABASE_PREFIX
from google.cloud import storage

DATASET_NAME = "validation"

client = bq_client()

def create_test_table():
  print("=============CREATING TABLE=============")
  # Construct a BigQuery client object.
  
  BQ_TABLE_NAME = "validation_table"

  dataset_id = f"{DATABASE_PREFIX}{DATASET_NAME}"
  dataset_prefix = f"{client.project}.{DATABASE_PREFIX}{DATASET_NAME}"
  # Construct a full Dataset object to send to the API.
  dataset = bigquery.Dataset(dataset_prefix)
  dataset.location = "US"
  
  # Send the dataset to the API for creation, with an explicit timeout.
  # Raises google.api_core.exceptions.Conflict if the Dataset already
  # exists within the project.
  dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
  print("Created dataset {}.{}".format(client.project, dataset.dataset_id))
  table_id = f"{client.project}.{dataset_id}.{BQ_TABLE_NAME}"
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
    "Created table {}.{}.{}".format(
      table.project, table.dataset_id, table.table_id)
  )


def delete_dataset():
  print("================DELETING DATASET=============")
  dataset_id = f"{client.project}.{DATABASE_PREFIX}{DATASET_NAME}"
  # Use the delete_contents parameter to delete a dataset and its contents.
  # Use the not_found_ok parameter to not receive an error if the dataset has already been deleted.
  client.delete_dataset(
    dataset_id, delete_contents=True, not_found_ok=True
  )  # Make an API request.

  print("Deleted dataset '{}'.".format(dataset_id))




