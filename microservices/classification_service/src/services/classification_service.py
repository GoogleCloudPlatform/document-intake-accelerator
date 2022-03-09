from services.ML_Classification.split_and_classify import DocClassifier
import os
import json

def predict_doc_type(case_id:str , uid:str ,gcs_url : str):
    """
    Fetches the model predictions and returns the output in a dictionary format
    
    Args: case_id:str, uid:str, gcs_url:str

    Returns: case_id, u_id, predicted_class, model_conf, model_endpoint_id
    """
    
    outfolder = os.path.join(os.path.dirname(__file__),"temp_files")
    if not os.path.exists(outfolder):
        os.mkdir(os.path.join(os.path.dirname(__file__),"temp_files"))
    
    classifier  = DocClassifier(case_id,uid,gcs_url,outfolder)
    
    doc_type = json.loads(classifier.execute_job())
    print(doc_type)
    return doc_type