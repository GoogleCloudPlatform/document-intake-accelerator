from logging import warning
from pdf_splitter import *
from vertex_predicitons import *
import json
from utils import *
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

    def __init__(self, client_id, uid, pdf_uri, out_folder, projectid='claims-processing-dev') -> None:
        if not pdf_uri.endswith('pdf'):
            print("Invalid input file. Require PDF file")
            exit(-1)
        
        self.client_id = client_id
        self.uid = uid

        self.pdf_path = f'{client_id}_{uid}_' + basename(pdf_uri)

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
            predictions = self.classifier.endpoint_image_classification(endpoint_id='4679565468279767040',  filename=img_path)
            

            output = {
                'client_id': self.client_id,
                'u_id': self.uid,
                'PDF_path': self.pdf_path,
                'predicted_class': predictions['displayNames'][0],
                'model_conf': predictions['confidences'][0],
                'model_endpoint_id': predictions['ids'][0]
            }

            # remove the image from local after prediction as it is of no use further
            os.remove(img_path)

            return json.dumps(output)
            
        except Exception as e:
            if os.path.exists(img_path):
                os.remove(img_path)
            print(e)
            return None

if __name__ == "__main__":
    pdf = 'gs://claim-processing-classification-dataset/Arizona_claim22.pdf'
    out = '/Users/sumitvaise/DOCAI/claims-processing/classification/data/images'

    clf = DocClassifier(0,0,pdf, out_folder=out)
    print(clf.execute_job(page_num=0))
