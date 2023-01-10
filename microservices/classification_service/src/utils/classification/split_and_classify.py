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
import common.config

"""Performs pdf splitting and classification on
first page
"""
# from utils.classification.pdf_splitter import PDFManager
from .download_pdf_gcs import download_pdf_gcs
import json
from google.cloud import documentai_v1 as documentai
import sys
from os.path import basename
from common.config import get_parser_config
from common.config import CLASSIFIER, CLASSIFICATION_CONFIDENCE_THRESHOLD, \
  CLASSIFICATION_UNDETECTABLE_DEFAULT_CLASS
from common.utils.logging_handler import Logger

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
      Logger.error('Invalid input file. Require PDF file')
      sys.exit()

    self.case_id = case_id
    self.uid = uid
    # self.endpoint_id = CLASSIFICATION_ENDPOINT_ID

    self.pdf_path = f'{out_folder}/{case_id}_{uid}_' + basename(pdf_uri)
    Logger.info('PDF at ' + self.pdf_path)
    Logger.info('Downloading PDF from GCS')
    Logger.info('PDF URI: ' + pdf_uri)

    self.blob = download_pdf_gcs(gcs_uri=pdf_uri, output_filename=self.pdf_path)
    self.doc_path = self.pdf_path
    # self.splitter = PDFManager(pdf_file=self.pdf_path, out_path=out_folder)
    # self.classifier = VertexPredictions(project_id=PROJECT_ID)

  def get_classification_predictions(self):
    # read parser details from configuration json file
    parsers_info = get_parser_config()
    parser_details = parsers_info.get(CLASSIFIER, None)
    if not parser_details:
      Logger.error(f"No classification parser defined, exiting classification")
      return None
    location = parser_details["location"]
    processor_id = parser_details["processor_id"]
    parser_name = parser_details["parser_name"]
    opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}

    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    # parser api end point
    # name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
    name = processor_id
    document = {
        "content": self.blob.download_as_bytes(),
        "mime_type": "application/pdf"
    }
    # Configure the process request
    request = {"name": name, "raw_document": document}
    Logger.info(f"Specialized parser extraction api called for processor {parser_name} with id={processor_id}")
    # send request to parser
    result = client.process_document(request=request)
    parser_doc_data = result.document

    scores = []
    labels = []

    for entity in parser_doc_data.entities:
      label = entity.type_.replace("/", "_")
      # if label in DOC_CLASS_CONFIG_MAP.keys():
      #   label = DOC_CLASS_CONFIG_MAP[label]
      score = entity.confidence
      Logger.info(f"Type = {label}, with confidence = {score}")
      scores.append(score)
      labels.append(label)
    # # Sample raw prediction_result
    # # {'scores': [0.0136728594, 0.0222843271, 0.908525527, 0.0222843271, 0.0332329459], 'labels': ['PayStub', 'Utility', 'UE', 'Claim', 'DL'],
    # 'key': '/opt/routes/temp_files/06_09_2022_01_59_10_temp_files\\7f2ec4ee-2d87-11ed-a71c-c2c2b7b788a8_7FvQ5G3dddti02sHbBhK_arizona-application-form_0.png'}
    prediction = {'scores': scores, 'labels': labels}
    return prediction


  def execute_job(self, page_num=0):
    """
    Run splitting and classification job

    Args:
    page_num (int): Page to extract from pdf. Defaults to 0.

    Returns:
        JSON: json object
    """

    try:
      # # contains output image path
      # img_path = self.splitter.split_save2img(page_num=page_num)
      #
      # print(f"split_save2img: {img_path}")

      prediction_result = self.get_classification_predictions()
      # prediction_result = self.classifier.get_classification_predications(
      #     endpoint_id=self.endpoint_id, filename=img_path)
      #
      # # Sample raw prediction_result
      # # {'scores': [0.0136728594, 0.0222843271, 0.908525527, 0.0222843271, 0.0332329459], 'labels': ['PayStub', 'Utility', 'UE', 'Claim', 'DL'], 'key': '/opt/routes/temp_files/06_09_2022_01_59_10_temp_files\\7f2ec4ee-2d87-11ed-a71c-c2c2b7b788a8_7FvQ5G3dddti02sHbBhK_arizona-application-form_0.png'}
      #
      print("prediction_result:")
      print(prediction_result)

      predicted_score = -1.0
      predicted_class = None
      for index, label in enumerate(prediction_result["labels"]):
        if prediction_result["scores"][index] > predicted_score:
          predicted_score = prediction_result["scores"][index]
          predicted_class = label

    # remove the image from local after prediction as it is of no use further
    # os.remove(img_path)
    # os.remove(self.pdf_path)

    except Exception as e:
      Logger.error(f"Error while getting predictions from classifier for {self.pdf_path}")
      Logger.error(e)

      # We will classify all documents as Claim (demo) Right Now when classifier not set
      Logger.warning(f"Falling back on the default class {CLASSIFICATION_UNDETECTABLE_DEFAULT_CLASS}")
      predicted_class = CLASSIFICATION_UNDETECTABLE_DEFAULT_CLASS
      predicted_score = 1.0

    print(f"predicted_class: {predicted_class}")
    print(f"predicted_score: {predicted_score}")

    # If confidence is greater than the threshold then it's a valid doc
    if predicted_score < CLASSIFICATION_CONFIDENCE_THRESHOLD:
      Logger.warning(f"Classifier could not pass the Classification Confidence threshhold, falling back on the default class {CLASSIFICATION_UNDETECTABLE_DEFAULT_CLASS}")
      predicted_class = CLASSIFICATION_UNDETECTABLE_DEFAULT_CLASS

    output = {
        'case_id': self.case_id,
        'u_id': self.uid,
        'predicted_class': predicted_class,
        'model_conf': predicted_score,
    }
    return json.dumps(output)
