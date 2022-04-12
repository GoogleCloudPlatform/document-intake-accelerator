"""GCS bucket move files function """
from google.cloud import storage
# disabling for linting to pass for blob_copy variable
# pylint: disable = unused-variable
def copy_blob(
    bucket_name, source_blob_name, destination_blob_name
):
  storage_client = storage.Client()
  source_bucket = storage_client.bucket(bucket_name)
  source_blob = source_bucket.blob(source_blob_name)
  destination_bucket = storage_client.bucket(bucket_name)
  blob_copy = source_bucket.copy_blob(
    source_blob, destination_bucket, destination_blob_name
  )
  source_bucket.delete_blob(source_blob_name)
  return  "success"
