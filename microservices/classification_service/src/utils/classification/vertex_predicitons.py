"""
Modules uses GCP Vertex AI to serve online predictions
"""
import base64
from importlib_metadata import os

from google.cloud import storage
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict


class VertexPredictions:
  """
  Class helps in getting predictions using VertexAI.
  This class does batch as well as online predictions on a trained model.
  Results are uploaded to a user specified bucket.
  """
  def __init__(self, project_id, location="us-central1",
    credentials_json=None) -> None:
    self.project_id = project_id
    self.loc = location
    self.credential = credentials_json


  def endpoint_image_classification(self, endpoint_id: str, filename: str,
    api_endpoint: str = "us-central1-aiplatform.googleapis.com"):

    """ Get prediction on images.

    Returns:
        _type_: _description_
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

    # The format of each instance should conform to the deployed
    # model's prediction input schema.
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    instance = predict.instance.ImageClassificationPredictionInstance(
      content=encoded_content).to_value()
    instances = [instance]
    parameters = predict.params.ImageClassificationPredictionParams(
      confidence_threshold=0.5, max_predictions=5,).to_value()
    endpoint = client.endpoint_path(
      project=self.project_id, location=self.loc, endpoint=endpoint_id
    )
    response = client.predict(
      endpoint=endpoint, instances=instances, parameters=parameters
    )
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
