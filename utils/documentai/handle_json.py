import argparse
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                             '../../microservices/extraction_service/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/src'))

from utils import extract_entities
from common.utils.format_data_for_bq import format_data_for_bq

def get_parser():
  # Read command line arguments
  args_parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      script to Load Returned JSON file and send to BigQuery.
      """,
      epilog="""
      Examples:

      python handle_json.py -f=gs-path-to-file.json.pdf
      """)

  args_parser.add_argument('-f', dest="file_path", help="Path to json file")
  args_parser.add_argument('-c', dest="doc_class", help="name of the document class",
                           default="generic_form")

  return args_parser



if __name__ == "__main__":
  parser = get_parser()
  args = parser.parse_args()

  file_path = args.file_path
  doc_class = args.doc_class

  # Opening JSON file
  with open(file_path, 'r') as openfile:

    # Reading from json file
    json_string = json.load(openfile)

    data = json.loads(json_string)

    desired_entities_list = extract_entities.specialized_parser_extraction_from_json(data, doc_class, "california")
    extraction_output = extract_entities.post_processing(desired_entities_list, doc_class, file_path, "True")

    is_tuple = isinstance(extraction_output, tuple)

    if is_tuple and isinstance(extraction_output[0], list):
      entities_for_bq = format_data_for_bq(extraction_output[0])
      print("Done!")

