"""Utility functions
"""

from google.cloud import storage

def download_file_gcs(bucket_name=None, gcs_uri=None,
                      file_to_download=None, output_filename=None):
  """Function takes a path of an object/file stored in GCS bucket and downloads
  the file in the current working directory

  Args:
      bucket_name (str): bucket name from where file to be downloaded
      gcs_uri (str): GCS object/file path
      output_filename (str): desired filename
      file_to_download (str): gcs file path excluding bucket name.
          Ex: if file is stored in X bucket under the folder Y with filename
          ABC.txt
          then file_to_download = Y/ABC.txt
  Return:
  """
  if bucket_name is None:
    bucket_name = gcs_uri.split('/')[2]

  # if file to download is not provided it can be extracted from the GCS URI
  if file_to_download is None and gcs_uri is not None:
    file_to_download = '/'.join(gcs_uri.split('/')[3:])

  storage_client = storage.Client()
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(file_to_download)

  if output_filename is None:
    output_filename = file_to_download
  with open(output_filename, 'wb') as file_obj:
    blob.download_to_file(file_obj)

  return output_filename
