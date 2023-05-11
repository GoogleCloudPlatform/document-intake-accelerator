import argparse
from google.cloud import storage
import os
gcs = storage.Client()


def copy_blob(bucket_name, source_blob_name, destination_blob_name,
    dest_bucket_name=None, delete_original=False):
  dest_bucket_name_str = bucket_name if not dest_bucket_name else dest_bucket_name
  print(f"--> Copying gs://{bucket_name}/{source_blob_name}  to "
              f"gs://{dest_bucket_name_str}/{destination_blob_name}")
  storage_client = storage.Client()
  source_bucket = storage_client.bucket(bucket_name)
  source_blob = source_bucket.blob(source_blob_name)
  if dest_bucket_name is None:
    destination_bucket = storage_client.bucket(bucket_name)
  else:
    destination_bucket = storage_client.bucket(dest_bucket_name)
  blob_copy = source_bucket.copy_blob(source_blob, destination_bucket,
                                      destination_blob_name)
  if delete_original:
    source_bucket.delete_blob(source_blob_name)
  return True


def copy(bucket_name_in, dir_in, bucket_name_out, dir_out, types):
  print(f"Copy with bucket_name_in={bucket_name_in}, dir_in={dir_in}, "
        f"bucket_name_out = {bucket_name_out},"
        f" dir_out = {dir_out},"
        f" types = {types}")

  if dir_in is not None and dir_in != "":
    blob_list = gcs.list_blobs(bucket_name_in, prefix=dir_in + "/")
  else:
    blob_list = gcs.list_blobs(bucket_name_in)

  for blob in blob_list:
    if not blob.name.endswith("/"):
      name = os.path.basename(blob.name)
      print(f"Handling {name}")
      for t in types:
        if t in name:
          print(f"--> Detected {t}, copying to gs://{bucket_name_out}/{dir_out}/{t}")
          copy_blob(bucket_name_in, blob.name, f"{dir_out}/{t}/{name}",
                    dest_bucket_name=bucket_name_out, delete_original=False)


def get_parser():
  # Read command line arguments
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      script to Test Document AI Classification.
      """,
      epilog="""
      Examples:

      python sort_copy.py -b_in=bucket-name -d_in=path/to/folder -t standard_form -t attachments -b_out=output_bucket -d_out=path/to/output/folder ]
      """)

  parser.add_argument('-b_in', dest="bucket_name_in", help="bucket name for input", required=True)
  parser.add_argument('-b_out', dest="bucket_name_out", help="bucket name for output")
  parser.add_argument('-d_in', dest="dir_in", help="path to folder", default=None)
  parser.add_argument('-d_out', dest="dir_out", help="path to output", default=None)

  parser.add_argument('-t', dest="types", help="substring to filter on", action="append", default=[])

  return parser

if __name__ == "__main__":
  parser = get_parser()
  args = parser.parse_args()

  bucket_name_in = args.bucket_name_in
  bucket_name_out = args.bucket_name_out
  if bucket_name_out is None:
    bucket_name_out = bucket_name_in

  dir_in = args.dir_in
  dir_out = args.dir_out

  if dir_out is None:
    dir_out = "sort_copy_output"

  types = args.types

  copy(bucket_name_in, dir_in, bucket_name_out, dir_out, types)