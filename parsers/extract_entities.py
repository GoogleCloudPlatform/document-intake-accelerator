import json
import os
import proto
import random
from google.cloud import documentai_v1 as documentai


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

    # These variables will be removed later
    project_id = "claims-processing-dev"  # later read this variable from project config files
    doc_path = os.path.join(doc_folder, doc)
    # print(project_id, location, processor_id, parser_name)

    opts = {}

    if location == "eu":
        opts = {"api_endpoint": "eu-documentai.googleapis.com"}

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    # Read the file into memory
    with open(doc_path, "rb") as image:
        image_content = image.read()

    document = {"content": image_content, "mime_type": "application/pdf"}

    # Configure the process request
    request = {"name": name, "raw_document": document}

    result = client.process_document(request=request)

    parser_doc_data = result.document

    # extract dl entities
    extracted_entity_dict = dl_entities_extraction(parser_doc_data)

    # save extracted entities json
    with open("{}.json".format(os.path.join(extracted_entities, doc.split('.')[0])), "w") as outfile:
        json.dump(extracted_entity_dict, outfile, indent=4)

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

    print("process completed")

    # exit()


def dl_entities_extraction(parser_doc_data):
    parser_doc_entities = parser_doc_data.entities
    # Read the entities from the processor

    # entities will vary based on parser
    temp_dict = {"text": "", "confidence": 0}
    entity_dict = {"Family Name": temp_dict, "Given Names": temp_dict, "Document Id": temp_dict, "Expiration Date": temp_dict,
                   "Date Of Birth": temp_dict, "Issue Date": temp_dict, "Address": temp_dict, "Portrait": temp_dict, "Name": temp_dict}

    for each_entity in parser_doc_entities:
        key, val, confidence = each_entity.type_, each_entity.mention_text, round(each_entity.confidence,2)
        entity_dict[key] = {"text": val, "confidence": confidence}

    entity_dict["Name"]["text"] = (entity_dict["Given Names"]["text"] + " " + entity_dict["Given Names"]["text"]).strip()
    entity_dict["Name"]["confidence"] = round((entity_dict["Given Names"]["confidence"] + entity_dict["Given Names"]["confidence"])/2, 2)

    return entity_dict


def get_text(doc_element: dict, document: dict):
    """
    Document AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
    """

    response = ""

    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    return response


if __name__ == "__main__":

    # Extract API Provides label and document
    label = "driver_license"
    # file_path = "ip_docs/arizona-driver-form-15-ocr.pdf"
    doc_folder = "ip_docs"
    parser_op = "parser-json"
    extracted_entities = "extracted-entities"

    # read ip doc folder
    inp_docs = os.listdir(doc_folder)
    random.shuffle(inp_docs)

    # Read json configuration file
    with open("parser_config.json", 'r') as j:

        parsers_info = json.loads(j.read())

        for each_doc in inp_docs:

            parser_information = parsers_info.get(label)

            # file_path = os.path.join(doc_folder, each_doc)

            # call parser api
            if parser_information:
                # print('parser available')
                doc_extract(parser_information, each_doc)
            else:
                # send to HITL Process
                print('parser not available for this document')
