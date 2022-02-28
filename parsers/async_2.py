# required imports
import os
import re
import json
from google.cloud import documentai_v1 as documentai
from google.cloud import storage
from arizona_application_mapping import APPLICATION_MAPPING_DICT

# project details
project_id = 'claims-processing-dev'
location = 'us'  # Format is 'us' or 'eu'
processor_id = '58d7348f7955db9c'  # Create processor in Cloud Console
gcs_input_uri = "gs://async_form_parser/input/Arizona3.pdf"
gcs_output_uri = "gs://async_form_parser"
gcs_output_uri_prefix = "test"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/claims-processing-dev-sa.json"


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
    confidence = doc_element.confidence
    return response, confidence


# main function for asynchronous calling in DOC AI
def batch_process_documents(
        project_id,
        location,
        processor_id,
        gcs_input_uri,
        gcs_output_uri,
        gcs_output_uri_prefix,
        timeout,
):
    opts = {}

    # Location can be 'us' or 'eu'
    if location == "eu":
        opts = {"api_endpoint": "eu-documentai.googleapis.com"}

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    destination_uri = f"{gcs_output_uri}/{gcs_output_uri_prefix}/"
    print(destination_uri)

    gcs_documents = documentai.GcsDocuments(
        documents=[{"gcs_uri": gcs_input_uri, "mime_type": "application/pdf"}]
    )

    # 'mime_type' can be 'application/pdf', 'image/tiff',
    # and 'image/gif', or 'application/json'
    input_config = documentai.BatchDocumentsInputConfig(gcs_documents=gcs_documents)

    # Where to write results
    output_config = documentai.DocumentOutputConfig(
        gcs_output_config={"gcs_uri": destination_uri}
    )

    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"


    # request for Doc AI
    request = documentai.types.document_processor_service.BatchProcessRequest(
        name=name, input_documents=input_config, document_output_config=output_config,
    )

    operation = client.batch_process_documents(request)

    # Wait for the operation to finish
    operation.result(timeout=timeout)

    # Results are written to GCS. Use a regex to find
    # output files
    match = re.match(r"gs://([^/]+)/(.+)", destination_uri)
    output_bucket = match.group(1)
    prefix = match.group(2)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(output_bucket)
    blob_list = list(bucket.list_blobs(prefix=prefix))

    extracted_entity_list = []
    required_entities_list = []

    state = "arizona"

    mapping_dict = APPLICATION_MAPPING_DICT["arizona"]

    # browse through output jsons
    for i, blob in enumerate(blob_list):
        # If JSON file, download the contents of this blob as a bytes object.
        if ".json" in blob.name:
            if "California" in blob.name:
                continue
            print('json file name', blob.name)

            blob_as_bytes = blob.download_as_bytes()

            document = documentai.types.Document.from_json(blob_as_bytes)
            print(f"Fetched file {i + 1}")

            # For a full list of Document object attributes, please reference this page:
            # https://cloud.google.com/document-ai/docs/reference/rpc/google.cloud.documentai.v1beta3#document

            # Read the text recognition output from the processor
            for page in document.pages:
                for form_field in page.form_fields:

                    field_name, field_name_confidence = get_text(form_field.field_name, document)
                    field_value, field_value_confidence = get_text(form_field.field_value, document)


                    if field_name in mapping_dict.keys():

                        temp_dict = {"key": mapping_dict[field_name], "value": field_value,
                                     "key_confidence": round(field_name_confidence, 2),
                                     "value_confidence": round(field_value_confidence, 2)}

                        required_entities_list.append(temp_dict)

                    temp_dict = {"key": field_name, "value": field_value, "key_confidence": round(field_name_confidence,2), "value_confidence": round(field_value_confidence,2)}

                    extracted_entity_list.append(temp_dict)

                    print("Extraction completed")
        else:
            print(f"Skipping non-supported file type {blob.name}")



    # save extracted entities json

    with open("/home/venkatakrishna/Documents/Q/projects/doc-ai-test/application-arizona/extracted-entities/without-noisy/{}.json".format("Arizona9"), "w") as outfile:
        json.dump(extracted_entity_list, outfile, indent=4)

    # Extract desired entities only

    with open("/home/venkatakrishna/Documents/Q/projects/doc-ai-test/application-arizona/extracted-entities/without-noisy/{}.json".format("Arizona9_desired"), "w") as outfile:
        json.dump(required_entities_list, outfile, indent=4)

batch_process_documents('claims-processing-dev', 'us', '58d7348f7955db9c',
                        "gs://async_form_parser/input/Arizona9.pdf", "gs://async_form_parser", "test", 300)

def del_gcs_folder():

    from google.cloud import storage
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('async_form_parser')
    blobs = bucket.list_blobs(prefix='test')

    for blob in blobs:
        blob.delete()

    print("Delete successful")


del_gcs_folder()

