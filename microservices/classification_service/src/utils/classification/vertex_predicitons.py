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

"""
Modules uses GCP Vertex AI to serve online predictions

https://cloud.google.com/vertex-ai/docs/predictions/online-predictions-automl#aiplatform_predict_image_classification_sample-python
"""
import base64, json
from importlib_metadata import os

from google.cloud import storage
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from common.config import REGOIN


class VertexPredictions:
  """
  Class helps in getting predictions using VertexAI.
  This class does batch as well as online predictions on a trained model.
  Results are uploaded to a user specified bucket.
  """

  def __init__(self,
               project_id,
               location=REGOIN,
               credentials_json=None) -> None:
    self.project_id = project_id
    self.loc = location
    self.credential = credentials_json

  def get_classification_predications(
      self,
      endpoint_id: str,
      filename: str,
      api_endpoint: str = f"{REGOIN}-aiplatform.googleapis.com"):
    """ Get prediction on images.

    Returns:
        _type_: _description_

    Sample JSON request
    {
        "instances": [
            {
                "key": "test",
                "image_bytes": {
                   "b64": "<YOUR_BASE64_IMG_DATA>"
                }
            }
        ],
        "parameters": {
            "confidenceThreshold": 0.5,
            "maxPredictions": 5
        }
    }
    """

    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}

    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and
    # can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(
        client_options=client_options)
    with open(filename, "rb") as f:
      file_content = f.read()

    print(f"filename = {filename}")

    # The format of each instance should conform to the deployed
    # model's prediction input schema.
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    print(f"encoded_content size: {len(encoded_content)}")

    instances = [{"key": filename, "image_bytes": {"b64": encoded_content}}]
    parameters = {"confidenceThreshold": 0.5, "maxPredictions": 5}
    endpoint = client.endpoint_path(
        project=self.project_id, location=self.loc, endpoint=endpoint_id)

    print("endpoint")
    print(json.dumps(endpoint))

    print("parameters")
    print(parameters)

    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters)
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)
    predictions = response.predictions
    return dict(predictions[0])

  def upload_tobucket(self, bucket_name, folder, file_name):
    """
    Upload files to bucket

    Args:
        bucket_name (str): bucket name
        folder (str): folder to upload in
        file_name (str): filename
    """
    client = storage.Client(project=self.project_id)
    bucket = client.get_bucket(bucket_name)
    upload_file_path = os.path.join(folder, file_name) if folder else file_name
    blob = bucket.blob(upload_file_path)
    blob.upload_from_filename(upload_file_path)
