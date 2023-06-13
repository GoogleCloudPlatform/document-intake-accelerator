"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import re

""" Process task api endpoint """
from fastapi import APIRouter, HTTPException
import traceback
import common.config
from common.utils.logging_handler import Logger
from common.config import get_config
from common.config import STATUS_SUCCESS, STATUS_ERROR
from google.cloud import documentai_v1 as documentai
from google.cloud import storage
storage_client = storage.Client()

PDF_MIME_TYPE = "application/pdf"

router = APIRouter()
SUCCESS_RESPONSE = {"status": STATUS_SUCCESS}
FAILED_RESPONSE = {"status": STATUS_ERROR}
from fastapi import BackgroundTasks
import asyncio

@router.get("/get_config")
async def get_config_by_name(name=None):
  """ reports document_types_config
          Returns:
              200 : fetches all the data from database
              500 : If any error occurs
    """

  try:
    # Fetching only active documents
    Logger.info(f"get_config called for {name}")
    config = get_config(name)
    Logger.info(f"get_config config={config}")
    response = SUCCESS_RESPONSE
    response["data"] = config
    return response

  except Exception as e:
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500, detail="Error in get_document_types_config") from e


async def batch_processing():
  doc_class = "generic_form"
  parser_details = common.config.get_parser_by_doc_class(doc_class)

  if parser_details:
    processor_path = parser_details["processor_id"]

    location = "us"
    if not location:
      Logger.error(f"Unidentified location for parser {processor_path}")
      return

    opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}

    dai_client = documentai.DocumentProcessorServiceClient(client_options=opts)
    processor = dai_client.get_processor(name=processor_path)
    print(
        f"parser_type={processor.type_}, parser_name={processor.display_name}")
  else:
    return {"message": "Parser Not Found"}
  gcs_documents = documentai.GcsDocuments(documents=[{
      "gcs_uri": "gs://ek-cda-engine-001-sample-forms/form.pdf",
      "mime_type": "application/pdf"
  }])

  input_config = documentai.BatchDocumentsInputConfig \
    (gcs_documents=gcs_documents)

  # create a temp folder to store parser op, delete folder once processing done
  # call create gcs bucket function to create bucket,
  # folder will be created automatically not the bucket
  gcs_output_uri = f"gs://ek-cda-engine-001-docai-output/extractor_out_test/"


  # Temp op folder location
  output_config = documentai.DocumentOutputConfig(
      gcs_output_config={"gcs_uri": gcs_output_uri})

  Logger.info(f"batch_extraction - input_config = {input_config}")
  Logger.info(f"batch_extraction - output_config = {output_config}")


  # request for Doc AI
  request = documentai.types.document_processor_service.BatchProcessRequest(
      name=processor.name,
      input_documents=input_config,
      document_output_config=output_config,
  )
  operation = dai_client.batch_process_documents(request)
  operation.add_done_callback(get_callback_fn(operation))


@router.get("/test")
async def test(background_task: BackgroundTasks):
  """Process task runs the ML pipeline

  Args:
    payload (ProcessTask): Consist of configs required to run the pipeline
    background_task : It is used to run the ML tasks in the background
    is_hitl : It is used to run the pipeline for unclassified documents
    is_reassign : It is used to run the pipeline for reassigned document
  Returns:
    202 : Documents are being processed
    422 : Invalid json provided
    """


  background_task.add_task(batch_processing)
  # background_task.add_task(test_async)
  return {"message": "Processing your document"}


async def extract(dai_client, request):
  print(f"Extraction Started for {request}")

  # t1 = asyncio.create_task(simple_coroutine())
  # t1.add_done_callback(post_process_extract)
  # await t1

  operation = dai_client.batch_process_documents(request)
  operation.add_done_callback(get_callback_fn(operation))
  # await operation
  print("Extraction - exiting")


def form_parser(future, operation, result):
  # Once the operation is complete,
  # get output document information from operation metadata
  print(f"form_parser = {future.result()}")
  result.append("Test")
  return
  metadata = documentai.BatchProcessMetadata(operation.metadata)
  if metadata.state != documentai.BatchProcessMetadata.State.SUCCEEDED:
    raise ValueError(
        f"batch_extraction - Batch Process Failed: {metadata.state_message}")

  documents = {}  # Contains per processed document, keys are path to original document

  # One process per Input Document
  blob_count = 0
  for process in metadata.individual_process_statuses:
    # output_gcs_destination format: gs://BUCKET/PREFIX/OPERATION_NUMBER/INPUT_FILE_NUMBER/
    # The Cloud Storage API requires the bucket name and URI prefix separately
    matches = re.match(r"gs://(.*?)/(.*)", process.output_gcs_destination)
    if not matches:
      print(
          f"batch_extraction - Could not parse output GCS destination:[{process.output_gcs_destination}]")
      continue

    output_bucket, output_prefix = matches.groups()
    output_gcs_destination = process.output_gcs_destination
    input_gcs_source = process.input_gcs_source
    print(
        f"batch_extraction - Handling DocAI results for {input_gcs_source} using "
        f"process output {output_gcs_destination}")
    # Get List of Document Objects from the Output Bucket
    output_blobs = storage_client.list_blobs(output_bucket,
                                             prefix=output_prefix + "/")

    # Document AI may output multiple JSON files per source file
    # Sharding happens when the output JSON File gets over a size threshold
    # (> 10MB, around 40 or 50 pages).
    for blob in output_blobs:
      # Document AI should only output JSON files to GCS
      if ".json" not in blob.name:
        Logger.warning(
            f"batch_extraction - Skipping non-supported file: {blob.name} - Mimetype: {blob.content_type}"
        )
        continue
      blob_count = blob_count + 1
      # Download JSON File as bytes object and convert to Document Object
      Logger.info(
          f"batch_extraction - Adding {blob_count} gs://{output_bucket}/{blob.name}")
      document = documentai.Document.from_json(
          blob.download_as_bytes(), ignore_unknown_fields=True
      )
      if input_gcs_source not in documents.keys():
        documents[input_gcs_source] = []
      documents[input_gcs_source].append(document)

  Logger.info(
      f"batch_extraction - Loaded {sum([len(documents[x]) for x in documents if isinstance(documents[x], list)])} DocAI document objects retrieved from json. ")

  return documents


def get_callback_fn(operation):
  def post_process_extract(future):
    print(f"post_process_extract - Extraction Complete!")
    print(f"post_process_extract - operation.metadata={operation.metadata}")

    result = []
    form_parser(future, operation, result)
    print(f"post_process_extract {result}")

  return post_process_extract


# A simple Python coroutine
async def simple_coroutine():
  print("Sleeping 10 seconds")
  await asyncio.sleep(10)
  return 1

async def my_callback(result):
    print("my_callback got:", result)
    return "My return value is ignored"


async def coro(number):
  await asyncio.sleep(number)
  return number + 1


async def add_success_callback(fut, callback):
  result = await fut
  await callback(result)
  return result

if __name__ == "__main__":
  # el = asyncio.new_event_loop()
  # asyncio.set_event_loop(el)
  # asyncio.run(batch_processing())

  loop = asyncio.get_event_loop()
  task = asyncio.ensure_future(batch_processing())
  task = add_success_callback(task, my_callback)
  response = loop.run_until_complete(task)
  print("response:", response)
  loop.close()

