# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# [START documentai_process_document]

# Following Needs to be set as environment variables:
# PROJECT_ID
# PROCESSOR_ID

import argparse
import os
import re
from typing import Any
from typing import Dict

import pandas as pd
from google.api_core.client_options import ClientOptions
from google.cloud import documentai

project_id = os.environ.get("PROJECT_ID", "")
if project_id != "":
  os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
assert project_id, "Env var PROJECT_ID is not set."

location = 'us'  # Format is 'us' or 'eu'
processor_id = os.environ.get("PROCESSOR_ID", "")  # Create processor before running sample
assert processor_id, "Env var PROCESSOR_ID is not set."

mime_type = 'application/pdf'  # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types
field_mask = "text,entities,pages.pageNumber"  # Optional. The fields to return in the Document object.
# file_path = os.path.join(os.path.dirname(__file__), '../sample_data/test/pa-form-42.pdf')


# TODO supporting mote than single Level of Label Nesting. for Now just one level nesting is supported
def get_key_values_dic(entity: documentai.Document.Entity,
    document_entities: Dict[str, Any],
    parent_key: str = None
) -> None:

  # Fields detected. For a full list of fields for each processor see
  # the processor documentation:
  # https://cloud.google.com/document-ai/docs/processors-list
  entity_key = entity.type_.replace("/", "_")
  confidence = entity.confidence
  normalized_value = getattr(entity, "normalized_value", None)

  if parent_key is not None and parent_key in document_entities.keys():
    key = parent_key
    new_entity_value = (
        entity_key,
        normalized_value.text if normalized_value else entity.mention_text,
        confidence
    )
  else:
    key = entity_key
    new_entity_value = (
        normalized_value.text if normalized_value else entity.mention_text,
        confidence
    )

  existing_entity = document_entities.get(key)
  if not existing_entity:
    document_entities[key] = []
    existing_entity = document_entities.get(key)

  if len(entity.properties) > 0:
    # Sub-labels (only down one level)
    for prop in entity.properties:
      get_key_values_dic(prop, document_entities, entity_key)
  else:
    existing_entity.append(new_entity_value)


def trim_text(text: str):
  """
  Remove extra space characters from text (blank, newline, tab, etc.)
  """
  return text.strip().replace("\n", " ")


def write_config(keys):
  print("-------- START Generated Configuration to use in extraction_config.py")
  print('"default_entities": {')
  for key in set(keys):
    key = clean_form_parser_keys(key)[:49]
    if len(key) >= 46:
      key = key[:-3] + '...'
    key_norm = ''.join(e for e in clean_form_parser_keys(key.lower().replace(" ", "_")[:25]) if e.isalnum() or e == "_")
    print(f'  "{key}": ["{key_norm}"],')
  print('}')
  print("-------- END")


def clean_form_parser_keys(text):
  """
    Cleaning form parser keys
    Parameters
    ----------
    text: original text before noise removal - removed spaces, newlines
    Returns: text after noise removal
    -------
  """
  # removing special characters from beginning and end of a string
  try:
    if len(text):
      text = text.strip()
      text = text.replace("\n", " ")
      text = re.sub(r"^\W+", "", text)
      last_word = text[-1]
      text = re.sub(r"\W+$", "", text)
    if last_word in [")", "]"]:
      text += last_word

  except: # pylint: disable=bare-except
    print("Exception occurred while cleaning keys")

  return text

def process_document_sample(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str
):

  print(f"Using project_id={project_id}, processor_id={processor_id} to extract data from file_path={file_path} ")
  # You must set the api_endpoint if you use a location other than 'us', e.g.:
  opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

  client = documentai.DocumentProcessorServiceClient(client_options=opts)

  # The full resource name of the processor, e.g.:
  # projects/{project_id}/locations/{location}/processors/{processor_id}
  name = client.processor_path(project_id, location, processor_id)
  # Make GetProcessor request
  processor = client.get_processor(name=name)

  # Print the processor information
  print(f"Processor Name: {processor.name}")
  print(f"Processor Display Name: {processor.display_name}")
  print(f"Processor Type: {processor.type_}")

  # Read the file into memory
  with open(file_path, "rb") as image:
    print("loading")
    image_content = image.read()

  # Load Binary Data into Document AI RawDocument Object
  raw_document = documentai.RawDocument(content=image_content,
                                        mime_type=mime_type)

  # Configure the process request
  request = documentai.ProcessRequest(
      name=name, raw_document=raw_document
  )

  result = client.process_document(request=request)

  # For a full list of Document object attributes, please reference this page:
  # https://cloud.google.com/python/docs/reference/documentai/latest/google.cloud.documentai_v1.types.Document
  parser_doc_data = result.document

  if processor.type_ == "FORM_PARSER_PROCESSOR":
    # handle FORM PARSER
    names = []
    name_confidence = []
    values = []
    value_confidence = []
    for page in parser_doc_data.pages:
      for field in page.form_fields:
        # Get the extracted field names
        names.append(trim_text(field.field_name.text_anchor.content))
        # Confidence - How "sure" the Model is that the text is correct
        name_confidence.append(field.field_name.confidence)

        values.append(trim_text(field.field_value.text_anchor.content))
        value_confidence.append(field.field_value.confidence)

    # Create a Pandas Dataframe to print the values in tabular format.
    write_config(names)
    df = pd.DataFrame(
        {
            "Field Name": names,
            "Field Name Confidence": name_confidence,
            "Field Value": values,
            "Field Value Confidence": value_confidence,
        }
    )

    print(df)
  elif processor.type_ == "CUSTOM_EXTRACTION_PROCESSOR": #Custom Extractor Processor
    # convert to json
    # json_string = proto.Message.to_json(parser_doc_data)
    # print("Extracted data:")
    # print(json.dumps(json_string))
    # data = json.loads(json_string)
    # parser_entities = data["entities"]
    # for each_entity in parser_entities:
    #   print(each_entity)
    #   key, val, confidence = each_entity.get("type", ""), \
    #                          each_entity.get("mentionText", ""), round(
    #                           each_entity.get("confidence", 0), 2)
    #   print(f" --------  key={key},value={val}")
    #   for prop in each_entity.get("properties", []):
    #     key, val, confidence = prop.get("type", ""), \
    #                            prop.get("mentionText", ""), round(
    #                            prop.get("confidence", 0), 2)
    #     print(f" *****   key={key},value={val}")


    document_entities: Dict[str, Any] = {}
    for entity in parser_doc_data.entities:
      get_key_values_dic(entity, document_entities)

    print("Value Extraction Results:")

    for key in document_entities.keys():
      if len(document_entities[key]) >= 3:
        print(f"{key}:")
        for entity in document_entities[key]:
            print(f"    - {entity[0]} = {entity[1]} ({entity[2]:.1%} confident)")

    print()
    print("---------------- START GENERATED CONFIGURATION to use in extraction_config.py")
    for key in document_entities.keys():
      if len(document_entities[key]) >= 3:
      #print(f"{key}:")
        for entity in document_entities[key]:
          val = clean_form_parser_keys(entity[0])
          print(f"\"{val}\": [\"{val}\"],")
    print("---------------- END GENERATED CONFIGURATION")
  elif processor.type_ == "CUSTOM_CLASSIFICATION_PROCESSOR":

    for entity in parser_doc_data.entities:
      entity_key = entity.type_.replace("/", "_")
      confidence = entity.confidence
      print(f"Type = {entity_key}, with confidence = {confidence}")


def get_parser():
  # Read command line arguments
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      Script used to generate config for Parser.
      """,
      epilog="""
      Examples:

      python gen_config_processor.py -f=path-to-form.pdf
      """)
  parser.add_argument(
      "-f",
      dest="file_path",
      help="Path to PDF form file")

  return parser


if __name__ == "__main__":
  parser = get_parser()
  args = parser.parse_args()

  if not args.file_path:
    parser.print_help()
    exit()
  process_document_sample(project_id,
                          location,
                          processor_id,
                          args.file_path,
                          mime_type)

# [END documentai_process_document]


