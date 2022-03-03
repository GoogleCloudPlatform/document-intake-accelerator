""" Upload file to gcs bucket function """

from common.config import BUCKET_NAME


def upload_file(case_id, uid, file):
  print(case_id + uid + file)
  print(BUCKET_NAME)
  return "success"


def upload_file_json(case_id, uid, file):
  print(case_id + uid + file)
  return "success"
