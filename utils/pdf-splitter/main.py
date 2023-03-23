# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module defines a CLI that uses Document AI to split a PDF document"""

import argparse
import os
import random
import string
import sys
from typing import Sequence
import re
import glob
import time

from google.api_core.exceptions import InternalServerError
from google.api_core.exceptions import RetryError
from google.cloud import documentai
from google.cloud import storage
import google.auth
from google.api_core.client_options import ClientOptions

from google.cloud.documentai import (
  Document,
  DocumentProcessorServiceClient,
  Processor,
  ProcessRequest,
  RawDocument,
)
from pikepdf import Pdf

sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/src'))
from common.utils import helper

DEFAULT_MULTI_REGION_LOCATION = "us"
DEFAULT_PROCESSOR_TYPE = "CUSTOM_SPLITTING_PROCESSOR"

PDF_MIME_TYPE = "application/pdf"
PDF_EXTENSION = ".pdf"

storage_client = storage.Client()


def batch_process_document(
    client: DocumentProcessorServiceClient,
    processor_name: str,
    gcs_input_uris: list,
    gcs_output_bucket: str,
    gcs_output_uri_prefix: str,
    field_mask: str = None,
    timeout: int = 400,
):
  # gcs_documents = documentai.GcsDocuments(documents=[{
  #     "gcs_uri": gcs_input_uri,
  #     "mime_type": input_mime_type
  # }])
  # input_config = documentai.BatchDocumentsInputConfig \
  #     (gcs_documents=gcs_documents)

  input_documents = []
  for doc in gcs_input_uris:
      # Cloud Storage URI for the Input Document
      input_documents.append(
          documentai.GcsDocument(
              gcs_uri=doc, mime_type=PDF_MIME_TYPE
          )
      )

  # Load GCS Input URI into a List of document files
  input_config = documentai.BatchDocumentsInputConfig(
      gcs_documents=documentai.GcsDocuments(documents=input_documents)
  )

  # NOTE: Alternatively, specify a GCS URI Prefix to process an entire directory
  #
  # gcs_input_uri = "gs://bucket/directory/"
  # gcs_prefix = documentai.GcsPrefix(gcs_uri_prefix=gcs_input_uri)
  # input_config = documentai.BatchDocumentsInputConfig(gcs_prefix=gcs_prefix)

  # Cloud Storage URI for the Output Directory
  # This must end with a trailing forward slash `/`
  destination_uri = f"gs://{gcs_output_bucket}/"
  if gcs_output_uri_prefix != "":
    destination_uri = f"{destination_uri}/{gcs_output_uri_prefix}/"

  # print(f"batch_process_documents with processor_name={processor_name} gcs_input_uri={gcs_input_uri} destination_uri={destination_uri}")
  gcs_output_config = documentai.DocumentOutputConfig.GcsOutputConfig(
      gcs_uri=os.path.join(destination_uri, "json"), field_mask=field_mask
  )

  # Where to write results
  output_config = documentai.DocumentOutputConfig(
    gcs_output_config=gcs_output_config)
  print(f"input_config = {input_config}")
  print(f"output_config = {output_config}")

  # The full resource name of the processor, e.g.:
  # projects/project_id/locations/location/processor/processor_id

  request = documentai.BatchProcessRequest(
      name=processor_name,
      input_documents=input_config,
      document_output_config=output_config,
  )

  # BatchProcess returns a Long Running Operation (LRO)
  operation = client.batch_process_documents(request)

  # Continually polls the operation until it is complete.
  # This could take some time for larger files
  # Format: projects/PROJECT_NUMBER/locations/LOCATION/operations/OPERATION_ID
  try:
    print(f"Waiting for operation {operation.operation.name} to complete...")
    operation.result(timeout=timeout)
  # Catch exception when operation doesn't finish before timeout
  except (RetryError, InternalServerError) as e:
    print(e.message)

  # NOTE: Can also use callbacks for asynchronous processing
  #
  # def my_callback(future):
  #   result = future.result()
  #
  # operation.add_done_callback(my_callback)

  # Once the operation is complete,
  # get output document information from operation metadata
  metadata = documentai.BatchProcessMetadata(operation.metadata)

  if metadata.state != documentai.BatchProcessMetadata.State.SUCCEEDED:
    raise ValueError(f"Batch Process Failed: {metadata.state_message}")

  # One process per Input Document
  for process in metadata.individual_process_statuses:
    # output_gcs_destination format: gs://BUCKET/PREFIX/OPERATION_NUMBER/INPUT_FILE_NUMBER/
    # The Cloud Storage API requires the bucket name and URI prefix separately
    matches = re.match(r"gs://(.*?)/(.*)", process.output_gcs_destination)
    if not matches:
      print(
        f"Could not parse output GCS destination:[{process.output_gcs_destination}]")
      continue

    output_bucket, output_prefix = matches.groups()
    input_gcs_source = process.input_gcs_source
    print(
      f"input_gcs_source = {input_gcs_source}, output_gcs_destination = {process.output_gcs_destination}")
    # Get List of Document Objects from the Output Bucket
    output_blobs = storage_client.list_blobs(output_bucket,
                                             prefix=output_prefix)

    # Document AI may output multiple JSON files per source file
    for blob in output_blobs:
      # Document AI should only output JSON files to GCS
      if ".json" not in blob.name:
        print(
            f"Skipping non-supported file: {blob.name} - Mimetype: {blob.content_type}"
        )
        continue

      # Download JSON File as bytes object and convert to Document Object
      print(f"Fetching gs://{blob.name}")
      document = documentai.Document.from_json(
          blob.download_as_bytes(), ignore_unknown_fields=True
      )
      dirs, file_name = helper.split_uri_2_path_filename(input_gcs_source)
      in_bucket, blob_name = helper.split_uri_2_bucket_prefix(input_gcs_source)

      tempfolder, local_file_name = download_from_gcs(in_bucket, blob_name)

      splitter_out = os.path.join(tempfolder, os.path.splitext(file_name)[0])
      split_pdf(document.entities, local_file_name, output_dir=splitter_out)
      upload_to_gcs(splitter_out, output_bucket,
                    os.path.join(gcs_output_uri_prefix,
                                 os.path.splitext(file_name)[0]))
      try:
        os.remove(tempfolder)
      except OSError as er:
        print(f"Error while deleting {tempfolder}, {er}")
        pass

      # For a full list of Document object attributes, please reference this page:
      # https://cloud.google.com/python/docs/reference/documentai/latest/google.cloud.documentai_v1.types.Document

      # Read the text recognition output from the processor
      # print("The document contains the following text:")
      # print(document.text)


def get_processor(
    client: DocumentProcessorServiceClient,
    project_id: str,
    multi_region_location: str,
    file_path: str,
    output_dir: str,
    processor_id: str,
) -> str:
  print(
    f"Using project_id={project_id}, processor_id={processor_id} to extract data from file_path={file_path} ")

  processor_name = client.processor_path(project_id, multi_region_location,
                                         processor_id)
  # # Make GetProcessor request
  processor = client.get_processor(name=processor_name)

  # Print the processor information
  print(f"Processor Name: {processor.name}")
  print(f"Processor Display Name: {processor.display_name}")
  print(f"Processor Type: {processor.type_}")

  print(
      "Using:\n"
      f'* Project ID: "{project_id}"\n'
      f'* Location: "{multi_region_location}"\n'
      f'* Processor Name "{processor_name}"\n'
      f'* Processor Id "{processor_name}"\n'
      f'* Input PDF "{file_path}"\n'
      f'* Output directory: "{output_dir}"\n'
  )
  return processor_name


def process_file_online(client, project_id, multi_region_location, file_path,
    processor_id, output_dir):
  processor_name = get_processor(client, project_id, multi_region_location,
                                 file_path, output_dir, processor_id)
  document = online_process(client, processor_name, file_path)

  document_json = write_document_json(document, file_path,
                                      output_dir=output_dir)
  print(f"Document AI Output: {document_json}")

  split_pdf(document.entities, file_path, output_dir=output_dir)

  print("Done.")
  return 0


def process_file_batch(client, project_id, multi_region_location, dir_path,
    processor_id, output_dir):
  processor_name = get_processor(client, project_id, multi_region_location,
                                 dir_path, output_dir, processor_id)

  in_bucket_name, in_prefix = helper.split_uri_2_bucket_prefix(dir_path)
  print(
    f"process_file_batch dir_path={dir_path} in_bucket_name={in_bucket_name} in_prefix={in_prefix}")
  blobs = storage_client.list_blobs(in_bucket_name, prefix=in_prefix)

  batch_size = 20
  out_bucket_name, out_prefix = helper.split_uri_2_bucket_prefix(output_dir)
  blob_uris = []

  # TODO send 5 requests a time
  for blob in blobs:
      uri = f"gs://{dir_path}/{blob.name}"
      print(f"Processing {uri} {blob.content_type}")
      if str(blob.name).endswith(".pdf"):
        blob_uris.append(f"gs://{in_bucket_name}/{blob.name}")
        if len(blob_uris) == batch_size:
          print(f"Sending batch of {len(blob_uris)} forms for batch processing:  {','.join(blob_uris)}")

          batch_process_document(client, processor_name,
                                 blob_uris,
                                 out_bucket_name,
                                 out_prefix)
          blob_uris = []

  if len(blob_uris) != 0:
    batch_process_document(client, processor_name,
                           blob_uris,
                           out_bucket_name,
                           out_prefix)
  # batch_process_document(client, processor_name,
  #                        dir_path,
  #                        out_bucket_name,
  #                        out_prefix)

  # print(f"Sending for batch processing {len(blob_uris)} documents")
  # batch_process_document(client, processor_name,
  #                        blob_uris,
  #                        out_bucket_name,
  #                        out_prefix)

  print("Done.")


def main(args: argparse.Namespace) -> int:
  """This project splits a PDF document using the Document AI API to identify split points"""
  start = time.time()

  if not args.project_id:
    _, project_id = google.auth.default()
    args.project_id = project_id

  if not args.file_uri and not args.dir_uri:
    print(f"Need to specify either -f <file> or -d <directory> location")
    parser.print_help()
    exit()

  client = DocumentProcessorServiceClient(
      client_options=ClientOptions(
          api_endpoint=f"{args.multi_region_location}-documentai.googleapis.com"
      )
  )

  if args.file_uri:
    if args.file_uri.startswith("gs://"):
      print("Not Yet Implemented: batch processing for a file on gcs... ")
    else:
      file_path = os.path.abspath(args.file_uri)
      if not args.output_dir:
        args.output_dir = os.path.dirname(file_path)
      if PDF_EXTENSION not in args.file_path:
        print(f"Input file {args.file_path} is not a PDF")
        return 1
      if not os.path.isfile(file_path):
        print(f"Could not find file at {file_path}")
        return 1
      process_file_online(client, args.project_id, args.multi_region_location,
                          file_path, args.processor_id, args.output_dir)

  if args.dir_uri:
    if args.dir_uri.startswith("gs://"):
      process_file_batch(client, args.project_id, args.multi_region_location,
                         args.dir_uri, args.processor_id, args.output_dir)
    else:
      print(
        "Not Yet Implemented: batch processing for a directory locally ... ")
      dir_path = os.path.abspath(args.dir_uri)

  elapsed = "{:.0f}".format(time.time() - start)
  print(f"Elapsed time for operation {elapsed} seconds")


def get_or_create_processor(
    client: DocumentProcessorServiceClient,
    project_id: str,
    location: str,
    processor_type: str,
) -> str:
  """
    Searches for a processor name for a given processor type.
    Creates processor if one doesn't exist
    """
  parent = client.common_location_path(project_id, location)

  for processor in client.list_processors(parent=parent):
    if processor.type_ == processor_type:
      # Processor names have the form:
      # `projects/{project}/locations/{location}/processors/{processor_id}`
      # See https://cloud.google.com/document-ai/docs/create-processor for more information.
      return processor.name

  print(
      f"No split processor found. "
      f'creating new processor of type "{processor_type}"',
  )
  processor = client.create_processor(
      parent=parent,
      processor=Processor(display_name=processor_type, type_=processor_type),
  )
  return processor.name


def online_process(
    client: DocumentProcessorServiceClient,
    processor_name: str,
    file_path: str,
    mime_type: str = PDF_MIME_TYPE,
) -> Document:
  """
    Call the specified processors process document API with the contents of
    # the input PDF file as input.
    """
  with open(file_path, "rb") as pdf_file:
    result = client.process_document(
        request=ProcessRequest(
            name=processor_name,
            raw_document=RawDocument(content=pdf_file.read(),
                                     mime_type=mime_type),
        )
    )
  return result.document


def write_document_json(document: Document, file_path: str,
    output_dir: str) -> str:
  """
    Write Document object as JSON file
    """

  # File Path: output_dir/file_name.json
  output_filepath = os.path.join(
      output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.json"
  )

  with open(output_filepath, "w", encoding="utf-8") as json_file:
    json_file.write(
        Document.to_json(document, including_default_value_fields=False)
    )

  return output_filepath


def upload_to_gcs(local_path, bucket_name, prefix):
  assert os.path.isdir(local_path)
  bucket = storage_client.bucket(bucket_name)
  for local_file in glob.glob(local_path + '/**'):
    if not os.path.isfile(local_file):
      upload_to_gcs(local_file, bucket,
                    prefix + "/" + os.path.basename(local_file))
    else:
      remote_path = os.path.join(prefix, local_file[1 + len(local_path):])
      blob = bucket.blob(remote_path)
      print(f"Uploading {local_path} to gs://{bucket_name}/{blob.name} ...")
      blob.upload_from_filename(local_file)


def download_from_gcs(bucket_name, source_blob_name):
  print(f"Downloading gs://{bucket_name}/{source_blob_name} locally .. ")
  bucket = storage_client.bucket(bucket_name)

  # Construct a client side representation of a blob.
  # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
  # any content from Google Cloud Storage. As we don't need additional data,
  # using `Bucket.blob` is preferred here.

  letters = string.ascii_lowercase
  temp_folder = "".join(random.choice(letters) for i in range(10))
  temp_folder = os.path.join(os.getcwd(), temp_folder)
  if not os.path.exists(temp_folder):
    print(f"Output directory used for extraction locally: {temp_folder}")
    os.mkdir(temp_folder)

  blob = bucket.blob(source_blob_name)
  # Download the file to a destination
  prefix, file_name = helper.split_uri_2_path_filename(source_blob_name)
  print(f"file_name={file_name}")
  destination_file_name = os.path.join(temp_folder, file_name)
  print(f"destination_file_name={destination_file_name}")
  blob.download_to_filename(destination_file_name)
  print(f"Downloaded {source_blob_name} to {destination_file_name}")
  return temp_folder, destination_file_name


def split_pdf(entities: Sequence[Document.Entity], file_path: str,
    output_dir: str):
  """
    Create subdocuments based on Splitter/Classifier output
    """
  with Pdf.open(file_path) as original_pdf:
    # Create New PDF for each SubDocument
    print(f"Total subdocuments: {len(entities)}")

    for index, entity in enumerate(entities):
      start = int(entity.page_anchor.page_refs[0].page)
      end = int(entity.page_anchor.page_refs[-1].page)
      subdoc_type = entity.type_ or "subdoc"
      confidence = float('%.2f' % entity.confidence)
      # confidence = entity.confidence
      if start == end:
        page_range = f"pg{start + 1}"
      else:
        page_range = f"pg{start + 1}-{end + 1}"

      output_filename = f"{page_range}_{subdoc_type}"

      print(
        f"Creating subdocument {index + 1}: {output_filename} (confidence: {confidence})")

      subdoc = Pdf.new()
      for page_num in range(start, end + 1):
        subdoc.pages.append(original_pdf.pages[page_num])

      if not os.path.exists(output_dir):
        os.mkdir(output_dir)

      subdoc.save(
          os.path.join(
              output_dir,
              f"{output_filename}_{os.path.basename(file_path)}",
          ),
          min_version=original_pdf.pdf_version,
      )


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Split a PDF document.")

  parser.add_argument('-d', dest="dir_uri",
                      help="Path to gs directory (gcs uri or local)")
  parser.add_argument('-f', dest="file_uri",
                      help="Path to file (gcs uri or local)")

  parser.add_argument(
      "-o", "--output-dir",
      help="directory to save sub-documents, default: input PDF directory",
  )
  parser.add_argument(
      "--project-id", help="Project ID to use to call the Document AI API"
  )
  parser.add_argument(
      "--multi-region-location",
      help="multi-regional location for document storage and processing",
      default=DEFAULT_MULTI_REGION_LOCATION,
  )
  parser.add_argument(
      "--processor-id",
      help='id of the processor used as splitter',
      required=True,
  )
  sys.exit(main(parser.parse_args()))
