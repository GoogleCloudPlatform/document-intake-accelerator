import json
from google.cloud import bigquery
from google.cloud import storage
from common.config import PATH
bigquery_client= bigquery.Client()
# bigquery_client=bq_client()


def read_json(path):
    """Function to read a json file directly from gcs"""
    print(f"path: {path}")
    bucket_name = path.split("/", 3)[2]
    file_path = path.split("/", 3)[3]
    print(f"bucket: {bucket_name}, file_path: {file_path}")
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_path)
    data = blob.download_as_string(client=None)
    data_dict = json.loads(data)
    return data_dict



# def load_json(filename):
#     '''
#     Given the file path, the json is loaded a dict variable and returned 
#     '''
#     file=open(filename)
#     data= json.load(file) 
#     return data

def get_values(documentlabel,cid,uid):
    '''
    These Values will come from the API when Ready
    '''
    #Sample Values
    path =PATH
    data=read_json(path)
    # merge_query,documentlabel = get_values()
    merge_query= " and cid='{}' and uid='{}' ".format(cid,uid)  
    validation_score = get_scoring(data,merge_query,documentlabel)
    # stats(data,validation_score,documentlabel)
    
    return validation_score


def get_scoring(data,merge_query,documentlabel):
    '''
    Fire the Rules on BQ table and calculate the Validation Scores
    '''
    print(f"data: {data}")
    validation_score = 0
    for i in data[documentlabel]:
        query = data[documentlabel][i] + merge_query
        # query=i+d
        print(query)
        Query_Results = bigquery_client.query((query))
        df = Query_Results.to_dataframe()
        print(df)
        validation_score = validation_score + len(df)
        
    return validation_score/len(data[documentlabel])


# def stats(data,validation_score,documentlabel):
#     print("Total Number of Validation Rules for this document were ", len(data[documentlabel]))
#     print("Number of Rules fired succesfully were " , int(validation_score))
#     print("The validation Score is ",validation_score/len(data[documentlabel]))



