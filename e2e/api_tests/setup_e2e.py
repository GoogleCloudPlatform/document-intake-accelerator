from common.db_client import bq_client
from google.cloud import bigquery
from common.config import PROJECT_ID,DATABASE_PREFIX

def create_table():
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

def delete_dataset():

    # Construct a BigQuery client object.
    client = bq_client()

    # TODO(developer): Set model_id to the ID of the model to fetch.
    dataset_id = f"{PROJECT_ID}.{DATABASE_PREFIX}"

    # Use the delete_contents parameter to delete a dataset and its contents.
    # Use the not_found_ok parameter to not receive an error if the dataset has already been deleted.
    client.delete_dataset(
        dataset_id, delete_contents=True, not_found_ok=True
    )  # Make an API request.

    print("Deleted dataset '{}'.".format(dataset_id))