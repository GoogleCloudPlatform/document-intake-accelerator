"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""Performs pdf splitting and classification on
first page
"""
from utils.classification.pdf_splitter import PDFManager
from utils.classification.vertex_predicitons import VertexPredictions
from utils.classification.download_pdf_gcs import download_pdf_gcs
# from common.config import CLASSIFICATION_CONFIDENCE_THRESHOLD, CLASSIFICATION_ENDPOINT_ID, PROJECT_ID
from common.config import PROJECT_ID
import json
import os
import sys
from os.path import basename
import warnings

warnings.filterwarnings('ignore')

CLASSIFICATION_UNDETECTABLE = "unclassified"


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
    # self.endpoint_id = CLASSIFICATION_ENDPOINT_ID

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

    # We will classify all documents as Prior-Auth Right Now
    predicted_class = "PriorAuth"
    predicted_score = 1.0
    # # contains output image path
    # img_path = self.splitter.split_save2img(page_num=page_num)
    #
    # print(f"split_save2img: {img_path}")
    #
    # prediction_result = self.classifier.get_classification_predications(
    #     endpoint_id=self.endpoint_id, filename=img_path)
    #
    # # Sample raw prediction_result
    # # {'scores': [0.0136728594, 0.0222843271, 0.908525527, 0.0222843271, 0.0332329459], 'labels': ['PayStub', 'Utility', 'UE', 'Claim', 'DL'], 'key': '/opt/routes/temp_files/06_09_2022_01_59_10_temp_files\\7f2ec4ee-2d87-11ed-a71c-c2c2b7b788a8_7FvQ5G3dddti02sHbBhK_arizona-application-form_0.png'}
    #
    # print("prediction_result:")
    # print(prediction_result)
    #
    # predicted_score = -1.0
    # predicted_class = None
    # for index, label in enumerate(prediction_result["labels"]):
    #   if prediction_result["scores"][index] > predicted_score:
    #     predicted_score = prediction_result["scores"][index]
    #     predicted_class = label

    print(f"predicted_class: {predicted_class}")
    print(f"predicted_score: {predicted_score}")

    # If confidence is greater than the threshold then its a valid doc
    # if predicted_score < CLASSIFICATION_CONFIDENCE_THRESHOLD:
    #   predicted_class = CLASSIFICATION_UNDETECTABLE

    output = {
        'case_id': self.case_id,
        'u_id': self.uid,
        'predicted_class': predicted_class,
        'model_conf': predicted_score,
    }

    # remove the image from local after prediction as it is of no use further
    # os.remove(img_path)
    # os.remove(self.pdf_path)
    return json.dumps(output)
