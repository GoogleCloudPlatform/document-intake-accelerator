from pdf_splitter import *
from vertex_predicitons import *
import json

class DocClassifier:
    """ Class uses PDF splitter to split the PDF into a separate pages 
        of image format and then runs the classification on the first page image.
        For classification it utilizes VertexAI online predictions.
    """

    def __init__(self, client_id, uid, pdf_path, out_folder, projectid='claims-processing-dev') -> None:
        self.client_id = client_id
        self.uid = uid

        self.doc_path = pdf_path
        self.splitter = PDFManager(pdf_file=pdf_path, out_path=out_folder)
        self.classifier = VertexPredictions(project_id=projectid)
    
    def execute_job(self):
        page_num=0 # front page

        img_path = self.splitter.split_save2img(page_num=0, save=True) # contains output image path
        predictions = self.classifier.endpoint_image_classification(endpoint_id='7305902922850631680',  filename=img_path)
        
        output = {
            'client_id': self.client_id,
            'u_id': self.uid,
            'img_path': img_path,
            'predicted_class': predictions['displayNames'][0],
            'model_conf': predictions['confidences'][0],
            'model_endpoint_id': predictions['ids'][0]
        }
        return json.dumps(output)

if __name__ == "__main__":
    pdf = '/Users/sumitvaise//Downloads/DocAI/Dataset/Arkansas/UE_forms/Arkansas2.pdf'
    out = '/Users/sumitvaise/DOCAI/claims-processing/classification/data/images'

    clf = DocClassifier(0,0,pdf, out_folder=out)
    print(clf.execute_job())
