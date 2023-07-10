from google.cloud import documentai_v1 as documentai

import common.config
from common.models import Document
from common.utils.helper import get_processor_location
from common.utils.logging_handler import Logger


def get_docai_input(processor_name: str, configs):
  Logger.info(f"get_docai_input - processor_name={processor_name}, "
              f"configs = {configs}")
  input_uris = []
  for config in configs:
    uid = config.get("uid")
    document = Document.find_by_uid(uid)
    if not document:
      Logger.warning(
          f"get_docai_input - Could not retrieve document by uid {uid}")
      continue
    input_uris.append(document.url)

  parser_details = common.config.get_parser_by_name(processor_name)

  if not parser_details:
    Logger.error(f"get_docai_input - Parser {processor_name} not defined in config")
    return None, None, None

  processor_path = parser_details["processor_id"]
  location = parser_details.get("location",
                                get_processor_location(processor_path))
  if not location:
    Logger.error(
        f"get_docai_input - Unidentified location for parser {processor_path}")
    return None, None, None

  opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}

  dai_client = documentai.DocumentProcessorServiceClient(
      client_options=opts)
  processor = dai_client.get_processor(name=processor_path)

  Logger.info(f"get_docai_input - processor={processor.name}, {processor.type_}"
              f"dai_client = {dai_client}, input_uris = {input_uris}")
  return processor, dai_client, input_uris
