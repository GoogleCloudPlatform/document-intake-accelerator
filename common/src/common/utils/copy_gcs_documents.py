"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""GCS bucket move files function """
from google.cloud import storage
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR


# disabling for linting to pass for blob_copy variable
# pylint: disable = unused-variable
def copy_blob(bucket_name, source_blob_name, destination_blob_name):
  storage_client = storage.Client()
  source_bucket = storage_client.bucket(bucket_name)
  source_blob = source_bucket.blob(source_blob_name)
  destination_bucket = storage_client.bucket(bucket_name)
  blob_copy = source_bucket.copy_blob(source_blob, destination_bucket,
                                      destination_blob_name)
  source_bucket.delete_blob(source_blob_name)
  return STATUS_SUCCESS
