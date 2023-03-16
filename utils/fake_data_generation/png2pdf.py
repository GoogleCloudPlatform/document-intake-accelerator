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

# script to convert png to pdf
import os
import argparse
from PIL import Image

import re


def get_parser():
  # Read command line arguments
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      script to convert png to pdf.
      """,
      epilog="""
      Examples:

      python generate_images.py --f=path-to-form.pdf
      """)
  parser.add_argument(
      "-d",
      dest="folder_dir",
      help="Path to input  directory with png files")
  parser.add_argument(
      "-o",
      dest="pdf_path",
      default="out_pdf",
      help="Path to out directory with PDF files")
  return parser


parser = get_parser()
args = parser.parse_args()

if not args.folder_dir:
  parser.print_help()
  exit()

folder_dir = args.folder_dir
pdf_path = args.pdf_path
ct = 1
image_list = []

for images in os.listdir(folder_dir):
  image_list.append(images)


def atoi(text):
  return int(text) if text.isdigit() else text


def natural_keys(text):
  '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
  return [atoi(c) for c in re.split(r'(\d+)', text)]


image_list.sort(key=natural_keys)
print(image_list)
print(len(image_list))

if not os.path.exists(pdf_path):
    os.mkdir(pdf_path)

for images in image_list:
  # check if the image ends with png
  if (images.endswith(".png")):
    name = folder_dir + "/" + images
    image_1 = Image.open(name)
    im_1 = image_1.convert('RGB')
    name_out = pdf_path + "/" + os.path.splitext(os.path.basename(images))[0] + '.pdf'
    print(f"{ct} Saving {name} as {name_out}")
    im_1.save(name_out)
    ct = ct + 1

print(f"Export pdf files to {pdf_path}")
