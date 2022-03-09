from logging import warning
from services.ML_Classification.pdf_splitter import *
from services.ML_Classification.vertex_predicitons import *
from services.ML_Classification.download_pdf_gcs import *

import json
import os
from os.path import basename
import warnings
warnings.filterwarnings("ignore")


class DocClassifier:
    """ Class uses PDF splitter to split the PDF into a separate pages 
        of image format and then runs the classification on the first page image.
        For classification it utilizes VertexAI online predictions.

        This class takes client id, unique id, pdf path in cloud storage bucket and google
        cloud project name for authentication.
        
        At the end of the execution, it return the predicted class, local path of the pdf to be used
        in other modules if needed and other attributes in the JSON format.
    """

    def __init__(self, case_id, uid, pdf_uri, out_folder, projectid='claims-processing-dev') -> None:
        if not pdf_uri.endswith('pdf'):
            print("Invalid input file. Require PDF file")
            exit(-1)
        
        self.case_id = case_id
        self.uid = uid

        self.pdf_path = f'{out_folder}\\{case_id}_{uid}_' + basename(pdf_uri)
        print("PDF at "+self.pdf_path)
        print("Downloading PDF from GCS ")
        print("PDF URI: ", pdf_uri)
        download_pdf_gcs(
        gcs_uri=pdf_uri,
        output_filename=self.pdf_path
    )
        self.doc_path = self.pdf_path
        self.splitter = PDFManager(pdf_file=self.pdf_path, out_path=out_folder)
        self.classifier = VertexPredictions(project_id=projectid)
        
    def execute_job(self, page_num=0):
        
        try:
            img_path = self.splitter.split_save2img(page_num=page_num, save=True) # contains output image path
            print(img_path)
            predictions = self.classifier.endpoint_image_classification(endpoint_id='4679565468279767040',  filename=img_path)
            print(predictions)
            output = {
                'case_id': self.case_id,
                'u_id': self.uid,
                'predicted_class': predictions['displayNames'][0],
                'model_conf': predictions['confidences'][0],
                'model_endpoint_id': predictions['ids'][0]
            }

            # remove the image from local after prediction as it is of no use further
            os.remove(img_path)
            os.remove(self.pdf_path)

            
            return json.dumps(output)
            
        except Exception as e:
            print(e)
            if os.path.exists(img_path):
                os.remove(img_path)
            if os.path.exists(self.pdf_path):
                os.remove(self.pdf_path)
            print(e)
            return None