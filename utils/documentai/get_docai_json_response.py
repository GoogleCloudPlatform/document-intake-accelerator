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
import proto
import json

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


def process_document_sample(
    project_id: str,
    location: str,
    processor_id: str,
    in_file_path: str,
    out_file_path: str,
    mime_type: str
):

  print(f"Using project_id={project_id}, processor_id={processor_id} to extract data from file_path={in_file_path} ")
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
  with open(in_file_path, "rb") as image:
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
  # convert to json
  json_string = proto.Message.to_json(parser_doc_data)
  json_object = json.dumps(json_string, indent=4)
  with open(out_file_path, "w") as outfile:
    outfile.write(json_object)
  print(f"Saved json file into {out_file_path}")

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
      dest="in_file_path",
      help="Path to PDF form file")
  parser.add_argument(
      "-o",
      dest="out_file_path",
      help="Path to JSON file")
  return parser


if __name__ == "__main__":
  parser = get_parser()
  args = parser.parse_args()

  if not args.in_file_path:
    parser.print_help()
    exit()

  if not args.out_file_path:
    args.out_file_path = "output.json"

  process_document_sample(project_id,
                          location,
                          processor_id,
                          args.in_file_path,
                          args.out_file_path,
                          mime_type)

# [END documentai_process_document]


