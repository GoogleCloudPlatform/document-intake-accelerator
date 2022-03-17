'''
This Script is Used to Calculate the Validation Score
'''

import json
from google.cloud import bigquery
from google.cloud import storage
from common.config import PATH

bigquery_client = bigquery.Client()


def read_json(path):
  """Function to read a json file directly from gcs
  Input :
    path:gcs file path
  Output :
    data_dict:json dictionary

  """

  bucket_name = path.split("/", 3)[2]
  file_path = path.split("/", 3)[3]
  client = storage.Client()
  bucket = client.get_bucket(bucket_name)
  blob = bucket.blob(file_path)
  data = blob.download_as_string(client=None)
  data_dict = json.loads(data)
  return data_dict


def get_values(documentlabel,cid,uid):
  '''
  These Values will come from the API when Ready
  Input:
    documentlabel: Document type
    cid : caseid
    uid : Uid of the document
  Output:
    Validation Score

  '''
  path=PATH
  data=read_json(path)
  merge_query= f"and cid ='{cid}' and uid='{uid}' "
  validation_score = get_scoring(data,merge_query,documentlabel)
  # stats(data,validation_score,documentlabel)
  
  return validation_score


def get_scoring(data,merge_query,documentlabel):
  '''
  Fire the Rules on BQ table and calculate the Validation Scores
  input:
    data : Rules dict
    merge_query : the addtional query part with case id and uid appended
    documentlabel: Document type
  output:
    validation score

  '''
  validation_score = 0
  for i in data[documentlabel]:
    query = data[documentlabel][i] + merge_query
    # query=i+d
    print(query)
    query_results = bigquery_client.query((query))
    df = query_results.to_dataframe()
    print(df)
    validation_score = validation_score + len(df)
  validation_score = validation_score/len(data[documentlabel])
  return validation_score/len(data[documentlabel])
  