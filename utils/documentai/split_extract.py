import argparse
import os
import sys

from utils import extract_entities
from common.utils import helper

PROJECT_ID = os.environ.get("PROJECT_ID", "")
print(f"PROJECT_ID={PROJECT_ID}")
print(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""))
os.environ["CONFIG_FILE"] = f"gs://{PROJECT_ID}-config/config.json"
os.environ["DEBUG"] = 'True'

def get_args():
  # Read command line arguments
  args_parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      script to Test Document AI Extraction.
      """,
      epilog="""
      Examples:

      python generate_images.py -f=gs-path-to-form.pdf
      """)

  args_parser.add_argument('-f', dest="file_uri", help="Path to gs uri")
  return args_parser


if __name__ == "__main__":
  parser = get_args()
  args = parser.parse_args()

  file_uri = args.file_uri


  if not file_uri:
    parser.print_help()
    exit()

  if file_uri:
    # Call Splitter/classifier
    process_file(file_uri, doc_class)

  if dir_uri:
    process_dir(dir_uri, doc_class)