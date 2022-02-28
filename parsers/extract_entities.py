import json
import os
import proto
import random
from google.cloud import documentai_v1 as documentai
from utils_functions import entities_extraction
from test import download_pdf_gcs


def doc_extract(parser_details: dict, doc: str):
    """
    Parameters
    ----------
    parser_details: it has parser info like id, name, loc, and etc
    doc_path

    Returns: Extracted json response coming from Parsers
    -------
    """

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id

    location = parser_details["location"]

    processor_id = parser_details["processor_id"]

    parser_name = parser_details["parser_name"]

    required_entities = parser_details["required_entities"]

    """
    dl_required_entities = ["Family Name", "Given Names", "Document Id", "Expiration Date", "Date Of Birth", "Issue Date",
                         "Address", "Name", "Sex"]

    utility_required_entities = ["invoice_id", "invoice_date", "due_date", "receiver_name", "service_address", "total_tax_amount",
                                            "supplier_account_number"]
    """
    # These variables will be removed later
    project_id = "claims-processing-dev"  # later read this variable from project config files
    doc_path = os.path.join(doc_folder, doc)
    # print(project_id, location, processor_id, parser_name)

    opts = {}

    if location == "eu":
        opts = {"api_endpoint": "eu-documentai.googleapis.com"}

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    blob = download_pdf_gcs(
        gcs_uri='gs://async_form_parser/input/arizona-driver-form-13.pdf'
    )

    document = {"content": blob.download_as_bytes(), "mime_type": "application/pdf"}
    """
    # Read the file into memory
    with open(doc_path, "rb") as image:
        image_content = image.read()

    document = {"content": image_content, "mime_type": "application/pdf"}
    """

    # Configure the process request
    request = {"name": name, "raw_document": document}

    result = client.process_document(request=request)

    parser_doc_data = result.document

    # convert to json
    json_string = proto.Message.to_json(parser_doc_data)
    data = json.loads(json_string)

    # Remove unnecessary information parser json response
    not_required_attributes_from_parser_response = ["textStyles", "textChanges", "revisions",
                                                    "pages.image"]

    # not_required_attributes_from_parser_response = []

    for each_attr in not_required_attributes_from_parser_response:
        if "." in each_attr:
            parent_attr, child_attr = each_attr.split(".")

            for idx in range(len(data.get(parent_attr, 0))):
                data[parent_attr][idx].pop(child_attr, None)
        else:
            data.pop(each_attr, None)

    # save parser op output
    with open("{}.json".format(os.path.join(parser_op, doc.split('.')[0])), "w") as outfile:
        json.dump(data, outfile)


    # extract dl entities
    extracted_entity_dict = entities_extraction(data, required_entities)

    # save extracted entities json
    with open("{}.json".format(os.path.join(extracted_entities, doc.split('.')[0])), "w") as outfile:
        json.dump(extracted_entity_dict, outfile, indent=4)


    print("process completed")

    # exit()




if __name__ == "__main__":

    # Extract API Provides label and document
    label = "driver_license"
    # file_path = "ip_docs/arizona-driver-form-15-ocr.pdf"
    doc_folder = "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/dl-docs/ip-docs/without-noisy"
    parser_op = "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/dl-docs/parser-json/without-noisy"
    extracted_entities = "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/dl-docs/extracted-entities/without-noisy"

    # read ip doc folder
    inp_docs = os.listdir(doc_folder)
    random.shuffle(inp_docs)

    # Read json configuration file
    with open("parser_config.json", 'r') as j:

        parsers_info = json.loads(j.read())

        for each_doc in inp_docs:

            parser_information = parsers_info.get(label)

            # file_path = os.path.join(doc_folder, each_doc)
            print("file", each_doc)
            # call parser api
            if parser_information:
                # print('parser available')
                doc_extract(parser_information, each_doc)
            else:
                # send to HITL Process
                print('parser not available for this document')

            # exit()