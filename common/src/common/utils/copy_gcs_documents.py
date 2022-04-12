from google.cloud import storage

def copy_blob(
    bucket_name, source_blob_name, destination_blob_name
):
  storage_client = storage.Client()
  source_bucket = storage_client.bucket(bucket_name)
  print("+++++++++++source_blob_name in func+++++++++++++++++++" , source_blob_name)
  source_blob = source_bucket.blob(source_blob_name)
  destination_bucket = storage_client.bucket(bucket_name)
  print("+++++++++++destination_blob_name in fun++++++++++++++++++",destination_blob_name)
  blob_copy = source_bucket.copy_blob(
    source_blob, destination_bucket, destination_blob_name
  )
  print("------After copy in func---------")
  source_bucket.delete_blob(source_blob_name)
  print("---------After delete in func-------------")
  return  "success"