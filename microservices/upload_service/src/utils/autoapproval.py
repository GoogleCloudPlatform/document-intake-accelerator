"""
This code is Used to check the approval status of a document
depending on the 3 different scores
"""
import json
from google.cloud import storage
from commmon.utils.logging_handler import Logger


def read_json(path):
  """
  Function to read a json file directly from gcs
  Input:
  path: gcs path of the json to be loaded
  Output:
  data_dict : dict consisting of the json output
  """
  bucket_name = path.split("/", 3)[2]
  file_path = path.split("/", 3)[3]
  client = storage.Client()
  bucket = client.get_bucket(bucket_name)
  blob = bucket.blob(file_path)
  data = blob.download_as_string(client=None)
  data_dict = json.loads(data)
  return data_dict


def get_values(
    validation_score, extraction_score, matching_score, document_label,
    document_type
):
  """
  Used to calculate the approval status of a document depending on the
  validation, extraction and Matching Score
  Input:
  validation_score : Validation Score
  extraction_score : Extraction Score
  matching_score : Matching Score
  Output:
  status : Accept/Reject or Review
  flag : Yes or no
  """
  data = read_json("gs://async_form_parser/Jsons/acpt.json")
  Logger.info(
    f"Validation_Score:{validation_score}, Extraction_score :"
    f"{extraction_score},Matching_Score:{matching_score},"
    f"DocumentLabel:{document_label},DocumentType:{document_type}"
  )
  if document_type in ("supporting_documents", "claims_form"):
    for i in data[document_label]:
      if i != "Reject":
        v_limit = data[document_label][i]["Validation_Score"]
        e_limit = data[document_label][i]["Extraction_Score"]
        m_limit = data[document_label][i]["Matching_Score"]
        print(v_limit, e_limit, m_limit)

        if (
            validation_score > v_limit
            and extraction_score > e_limit
            and matching_score > m_limit
        ):
          flag = "yes"
          status = "Approved"
          return status, flag
      else:
        v_limit = data[document_label][i]["Validation_Score"]
        e_limit = data[document_label][i]["Extraction_Score"]
        m_limit = data[document_label][i]["Matching_Score"]
        flag = "no"
        if (
            validation_score > v_limit
            and extraction_score > e_limit
            and matching_score > m_limit
        ):
          status = "Review"
          Logger.info(f"Status :{status}")
          return status, flag
        else:
          status = "Reject"
          Logger.info(f"Status :{status}")

          return status, flag
  elif document_type == "application_form":
    for i in data[document_label]:
      if i != "Reject":
        e_limit = data[document_label][i]["Extraction_Score"]
        if extraction_score > e_limit:
          flag = "yes"
          status = "Approved"
          Logger.info(f"Status :{status}")

          return status, flag
      else:
        e_limit = data[document_label][i]["Extraction_Score"]
        flag = "no"
        if extraction_score > e_limit:
          status = "Review"
          Logger.info(f"Status :{status}")
          return status, flag
        else:
          status = "Reject"
          Logger.info(f"Status :{status}")

          return status, flag
