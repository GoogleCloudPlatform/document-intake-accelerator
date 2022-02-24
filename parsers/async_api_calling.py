import os
import re
from google.cloud import documentai_v1beta3 as documentai
from google.cloud import storage
import pandas as pd


# TODO(developer): Fill these variables with your values before running the sample
# PROJECT_ID = "YOUR_PROJECT_ID_HERE"
PROJECT_ID = "claims-processing-dev"
LOCATION = "us"  # Format is 'us' or 'eu'
PROCESSOR_ID = "58d7348f7955db9c"  # Create processor in Cloud Console

GCS_INPUT_BUCKET = 'async_form_parser/input'
GCS_INPUT_PREFIX = 'documentai/async_forms/'
GCS_OUTPUT_URI = 'async_form_parser'
GCS_OUTPUT_URI_PREFIX = 'output'
TIMEOUT = 9999999999
GCS_IP_URI = "gs://async_form_parser/input/California1.pdf"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "claims-processing-dev-sa.json"

def process_document_sample():

    # Instantiates a client
    client_options = {"api_endpoint": "{}-documentai.googleapis.com".format(LOCATION)}
    client = documentai.DocumentProcessorServiceClient(client_options=client_options)

    storage_client = storage.Client()

    # blobs = storage_client.list_blobs(GCS_INPUT_BUCKET, prefix=GCS_INPUT_PREFIX)


    document_configs = []
    print("Input Files:")

    """
    for blob in blobs:
        if ".pdf" in blob.name:
            source = "gs://{bucket}/{name}".format(bucket=GCS_INPUT_BUCKET, name=blob.name)
            print(source)
            document_config = {"gcs_uri": source, "mime_type": "application/pdf"}
            document_configs.append(document_config)
    """

    document_config = {"gcs_uri": GCS_IP_URI, "mime_type": "application/pdf"}
    document_configs.append(document_config)

    gcs_documents = documentai.GcsDocuments(
        documents=document_configs
    )

    input_config = documentai.BatchDocumentsInputConfig(gcs_documents=gcs_documents)

    destination_uri = f"{GCS_OUTPUT_URI}/{GCS_OUTPUT_URI_PREFIX}/"

    # Where to write results
    output_config = documentai.DocumentOutputConfig(
        gcs_output_config={"gcs_uri": destination_uri}
    )

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first.
    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}"
    request = documentai.types.document_processor_service.BatchProcessRequest(
        name=name,
        input_documents=input_config,
        document_output_config=output_config,
    )

    operation = client.batch_process_documents(request)

    # Wait for the operation to finish
    operation.result(timeout=TIMEOUT)

    # Results are written to GCS. Use a regex to find
    # output files
    match = re.match(r"gs://([^/]+)/(.+)", destination_uri)
    output_bucket = match.group(1)
    prefix = match.group(2)

    bucket = storage_client.get_bucket(output_bucket)
    blob_list = list(bucket.list_blobs(prefix=prefix))

    for i, blob in enumerate(blob_list):
        # If JSON file, download the contents of this blob as a bytes object.
        if ".json" in blob.name:
            blob_as_bytes = blob.download_as_string()
            print("downloaded")

            document = documentai.types.Document.from_json(blob_as_bytes)
            print(f"Fetched file {i + 1}")

            # For a full list of Document object attributes, please reference this page:
            # https://cloud.google.com/document-ai/docs/reference/rpc/google.cloud.documentai.v1beta3#document
            document_pages = document.pages
            keys = []
            keysConf = []
            values = []
            valuesConf = []

            # Grab each key/value pair and their corresponding confidence scores.
            for page in document_pages:
                for form_field in page.form_fields:
                    fieldName = get_text(form_field.field_name, document)
                    keys.append(fieldName.replace(':', ''))
                    nameConfidence = round(form_field.field_name.confidence, 4)
                    keysConf.append(nameConfidence)
                    fieldValue = get_text(form_field.field_value, document)
                    values.append(fieldValue.replace(':', ''))
                    valueConfidence = round(form_field.field_value.confidence, 4)
                    valuesConf.append(valueConfidence)

            # Create a Pandas Dataframe to print the values in tabular format.
            df = pd.DataFrame({'Key': keys, 'Key Conf': keysConf, 'Value': values, 'Value Conf': valuesConf})
            # display(df)
            print(df.head())

        else:
            print(f"Skipping non-supported file type {blob.name}")


# Extract shards from the text field
def get_text(doc_element: dict, document: dict):
    """
    Document AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    return response

doc = process_document_sample()