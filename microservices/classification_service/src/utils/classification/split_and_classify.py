"""Performs pdf splitting and classification on
first page
"""
from utils.classification.pdf_splitter import PDFManager
from utils.classification.vertex_predicitons import VertexPredictions
from utils.classification.download_pdf_gcs import download_pdf_gcs
from common.config import CONF_THRESH, CLASSIFICATION_ENDPOINT_ID, PROJECT_ID
import json
import os
import sys
from os.path import basename
import warnings

warnings.filterwarnings('ignore')


class DocClassifier:
  """
  Class uses PDF splitter to split the PDF into a separate pages
  of image format and then runs the classification on the first page image.
  For classification it utilizes VertexAI online predictions.

  This class takes client id, unique id, pdf path in cloud storage bucket
  and google cloud project name for authentication.

  At the end of the execution, it return the predicted class, local path of
  the pdf to be used in other modules if needed and other attributes in the
  JSON format.
  """

  def __init__(self, case_id, uid, pdf_uri, out_folder) -> None:
    if not pdf_uri.endswith('pdf'):
      print('Invalid input file. Require PDF file')
      sys.exit()

    self.case_id = case_id
    self.uid = uid
    self.conf = CONF_THRESH
    self.endpoint_id = CLASSIFICATION_ENDPOINT_ID

    self.pdf_path = f'{out_folder}\\{case_id}_{uid}_' + basename(pdf_uri)
    print('PDF at ' + self.pdf_path)
    print('Downloading PDF from GCS')
    print('PDF URI: ', pdf_uri)

    download_pdf_gcs(gcs_uri=pdf_uri, output_filename=self.pdf_path)
    self.doc_path = self.pdf_path
    self.splitter = PDFManager(pdf_file=self.pdf_path, out_path=out_folder)
    self.classifier = VertexPredictions(project_id=PROJECT_ID)

  def execute_job(self, page_num=0):
    """
    Run splitting and classification job

    Args:
    page_num (int): Page to extract from pdf. Defaults to 0.

    Returns:
        JSON: json object
    """

    # contains output image path
    img_path = self.splitter.split_save2img(page_num=page_num)
    print(img_path)
    predictions = self.classifier.endpoint_image_classification(
        endpoint_id=self.endpoint_id, filename=img_path)

    # If confidence is greater than the threshold then its a valid doc
    predicted_class = predictions['displayNames'][0]
    if predictions['confidences'][0] < self.conf:
      predicted_class = 'Negative'

    output = {
        'case_id': self.case_id,
        'u_id': self.uid,
        'predicted_class': predicted_class,
        'model_conf': predictions['confidences'][0],
        'model_endpoint_id': predictions['ids'][0]
    }

    # remove the image from local after prediction as it is of no use further
    os.remove(img_path)
    os.remove(self.pdf_path)

    return json.dumps(output)
