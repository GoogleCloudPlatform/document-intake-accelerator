'''
This code is Used to check the approval status of a document depending on the 3 different scores
'''

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



def get_values(validation_score,extraction_score,matching_score):
    '''
    Used to calculate the approval status of a document depending on the validation, extraction and Matching Score
    Input:
        validation_score : Validation Score 
        extraction_score : Extraction Score
        matching_score : Matching Score
    
    Output:
        status : Accept/Reject or Review
        flag : Yes or no
    '''
    data = read_json("gs://async_form_parser/Jsons/approval_rules.json")
    for i in data:
        if i!='Reject':
            v_limit = data[i]['Validation_Score']
            e_limit = data[i]['Extraction_Score']
            m_limit  = data[i]['Matching_Score']
            if validation_score > v_limit and extraction_score > e_limit and matching_score > m_limit:
                flag = "Yes"
                status = 'Approved'
                return status,flag
        else:
            flag= "no"
            v_limit = data[i]['Validation_Score']
            e_limit = data[i]['Extraction_Score']
            m_limit  = data[i]['Matching_Score']
            if validation_score > v_limit and extraction_score > e_limit and matching_score > m_limit:
                status = 'Review'
                return status,flag
            else:
                status = 'Reject'
                return status,flag
            