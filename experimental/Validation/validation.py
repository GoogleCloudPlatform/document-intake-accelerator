import json
from google.cloud import bigquery
bigquery_client = bigquery.Client()

def load_json(filename):
    '''
    Given the file path, the json is loaded a dict variable and returned 
    '''
    file=open(filename)
    data= json.load(file) 
    return data

def get_values():
    '''
    These Values will come from the API when Ready
    '''
    #Sample Values
    
    documentlabel = 'DriverLicense'
    cid = '897'
    uid = '986'
    merge_query= " and cid='{}' and uid='{}' ".format(cid,uid)  
    return merge_query,documentlabel
    
def get_scoring(data,merge_query,documentlabel):
    '''
    Fire the Rules on BQ table and calculate the Validation Scores
    '''
    validation_score = 0
    for i in data[documentlabel]:
        query = data[documentlabel][i] + merge_query
        # query=i+d
        print(query)
        Query_Results = bigquery_client.query((query))
        df = Query_Results.to_dataframe()
        print(df)
        validation_score = validation_score + len(df)
        
    return validation_score


def stats(data,validation_score,documentlabel):
    print("Total Number of Validation Rules for this document were ", len(data[documentlabel]))
    print("Number of Rules fired succesfully were " , int(validation_score))
    print("The validation Score is ",validation_score/len(data[documentlabel]))

def main():
    data=load_json('test.json')
    merge_query,documentlabel = get_values()
    validation_score = get_scoring(data,merge_query,documentlabel)
    stats(data,validation_score,documentlabel)

if __name__ == "__main__":
    main()


     