from google.cloud import storage
from google.cloud import aiplatform
from importlib_metadata import os
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
import base64

class VertexPredictions:

    """ Class helps in getting predictions using VertexAI.
        This class does batch as well as online predictions on a trained model.
        Results are uploaded to a user specified bucket.
    """
    def __init__(self, project_id, location='us-central1', credentials_json=None) -> None:
        self.project_id=project_id
        self.loc=location
        self.credential= credentials_json
        

    def endpoint_image_classification(self,endpoint_id: str,  filename: str, location: str = "us-central1", api_endpoint: str = "us-central1-aiplatform.googleapis.com"):
        # The AI Platform services require regional API endpoints.
        client_options = {"api_endpoint": api_endpoint}

        # Initialize client that will be used to create and send requests.
        # This client only needs to be created once, and can be reused for multiple requests.
        client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
        with open(filename, "rb") as f:
            file_content = f.read()

        # The format of each instance should conform to the deployed model's prediction input schema.
        encoded_content = base64.b64encode(file_content).decode("utf-8")
        instance = predict.instance.ImageClassificationPredictionInstance(content=encoded_content).to_value()
        instances = [instance]
        
        # See gs://google-cloud-aiplatform/schema/predict/params/image_classification_1.0.0.yaml for the format of the parameters.
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
        # See gs://google-cloud-aiplatform/schema/predict/prediction/image_classification_1.0.0.yaml for the format of the predictions.
        predictions = response.predictions
        return dict(predictions[0])
        # for prediction in predictions:
        #     print(" prediction:", dict(prediction))


    def get_batch_predictions(self, job_name, gcs_inp_jsonl_path, gcs_outpath, model_id="2155997166533869568"):
        MODEL_ID=model_id #"2155997166533869568"

        aiplatform.init(project=self.project_id, location=self.loc)
        model = aiplatform.Model(MODEL_ID)

        batch_prediction_job = model.batch_predict(
            job_display_name=job_name,
            machine_type='n1-standard-4',
            gcs_source=gcs_inp_jsonl_path, #,
            gcs_destination_prefix=gcs_outpath #
        )

    def create_bucket(self,bucket_name:str):
        pass

    def upload_tobucket(self, bucket_name, folder, file_name):
        client = storage.Client(project=self.project_id)
        bucket = client.get_bucket(bucket_name)
        upload_file_path = os.path.join(folder, file_name) if folder else file_name
        blob = bucket.blob(upload_file_path)
        blob.upload_from_filename(upload_file_path)

if __name__ =="__main__":
    vertex_predictor = VertexPredictions(project_id='claims-processing-dev')

    img_path = "/Users/sumitvaise//Downloads/DocAI/Dataset/Final/04_02_2022_11_16_28_Arkansas9_0.png"
    predictions = vertex_predictor.endpoint_image_classification(endpoint_id='7305902922850631680',  filename=img_path)
    print(type(predictions))


