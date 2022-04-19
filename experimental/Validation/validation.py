'''
This Script is Used to Calculate the Validation Score
'''

import json
import requests
import pandas as pd
from google.cloud import storage
from googleapiclient.errors import HttpError
from common.config import PATH,VALIDATION_TABLE

from common.utils.logging_handler import Logger
from db_client import bq_client

bigquery_client = bq_client()


def get_final_scores(dataList,entity):
  keys = []
  for d in dataList:
      keys.extend(list(d.keys()))

  repeating = dict()
  for key in keys:
         repeating[key] = keys.count(key)
  avg = dict()
  for key,value in repeating.items():
      avg[key] = sum(d.get(key) for d in dataList if d.get(key) ) / value
  for i in entity:
    i["validation_score"] = None
    
  for j,k in avg.items():
    for i in entity:
      if i["entity"] == j:
        i["validation_score"] = k
  return entity


def read_json(path):
  """Function to read a json file directly from gcs
  Input :
  path:gcs file path
  Output:
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


def get_values(documentlabel,cid,uid,entity):
  '''
  These Values will come from the API when Ready
  Input:
  documentlabel: Document type
  cid : caseid
  uid : Uid of the document
  Output:
  Validation Score

  '''
  # path=PATH
  try:
    # VALIDATION_TABLE = "claims-processing-dev.data_extraction.entities"
    # path = "gs://async_form_parser/Jsons/trial44.json"
    path=PATH
    data=read_json(path)
    merge_query= f"and case_id ='{cid}' and uid='{uid}'"
    validation_score,final_dict = \
    get_scoring(data,merge_query,documentlabel,VALIDATION_TABLE,entity)
    Logger.info(f"Validation completed for document with case id {cid}"
        f"and uid {uid}")
  except Exception as e:
    Logger.error(e)
    validation_score = None
    return validation_score
  return validation_score,final_dict


def get_individual_dict(query):
  dict1={}
  counter = query.count("$")
  for i in range(1,counter+1):
    key = query.split("$.")[i].split("'")[0]
    dict1[key] = None
  return dict1
  
  
def get_scoring(data,merge_query,documentlabel,VALIDATION_TABLE,entity):
  '''
  Fire the Rules on BQ table and calculate the Validation Scores
  input:
  data : Rules dict
  merge_query : the addtional query part with case id and uid appended
  documentlabel: Document type
  output:
  validation score
  '''
  l2=[]
  validation_score = 0
  for i in data[documentlabel]:
    query = data[documentlabel][i] + merge_query
    query = query.replace("project_table",VALIDATION_TABLE)
    dict1=get_individual_dict(query)
    try:
        query_results = bigquery_client.query((query))
        df = query_results.to_dataframe()
    except Exception as e:
        Logger.error(e)
        df = pd.DataFrame()
    df = df.drop_duplicates()
    validation_score = validation_score + len(df)
    for key in dict1:
        dict1[key] = len(df)
    l2.append(dict1)
  validation_score = validation_score/len(data[documentlabel])
  final_dict = get_final_scores(l2,entity)
  return validation_score,final_dict


