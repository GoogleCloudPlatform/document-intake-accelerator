import json
import os
import proto
from google.cloud import documentai_v1 as documentai


def doc_extract(parser_details: dict, doc_path: str):
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
    # project_id = parser_details["project_name"]
    project_id = os.environ['GCP_PROJECT']  # later read this variable from project config files

    print(project_id, location, processor_id, parser_name)

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

    json_string = proto.Message.to_json(result.document)
    data = json.loads(json_string)

    # Remove unnecessary information parser json response
    not_required_attributes_from_parser_response = ["textStyles", "textChanges", "revisions",
                                                    "pages.image"]

    for each_attr in not_required_attributes_from_parser_response:
        if "." in each_attr:
            parent_attr, child_attr = each_attr.split(".")

            for idx in range(len(data.get(parent_attr, 0))):
                data[parent_attr][idx].pop(child_attr, None)

        else:
            data.pop(each_attr, None)

    # save output to json

    with open("{}.json".format(doc_path.split('.')[0]), "w") as outfile:
        json.dump(data, outfile)

    print("process completed")

    exit()

    document_pages = document.pages

    # Read the text recognition output from the processor
    print("The document contains the following paragraphs:")
    for page in document_pages:
        paragraphs = page.paragraphs
        for paragraph in paragraphs:
            print(paragraph)
            paragraph_text = get_text(paragraph.layout, document)
            print(f"Paragraph text: {paragraph_text}")


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
    label = "DriverLicense_2"
    file_path = "arizona-driver-form-15-ocr.pdf"

    # Read json configuration file
    with open("parser_selection.json", 'r') as j:

        parsers_info = json.loads(j.read())

        parser_information = parsers_info.get(label)

        # call parser api to get response
        if parser_information:
            print('parser available')
            doc_extract(parser_information, file_path)
        else:
            # send to HITL Process
            print('parser not available for this document')
