import asyncio
from pyppeteer import launch
import csv
import json
import argparse
import time
import pathlib
import re
import random
from datetime import datetime


async def run_browser(config, data_list, **options):
  browser = await launch()
  page = await browser.newPage()
  debug = options.get("debug", False)
  output_folder = options.get("output_folder", "./")

  for index, data_row in enumerate(data_list):
    screenshot_filename = output_folder + "/" + \
      config.get("image_name_prefix", "image-") + str(index + 1) + ".png"

    print(f"Generating image for row #{index + 1}: {screenshot_filename}")
    if debug:
      print(data_row)

    await run_page(page, config, data_row, screenshot_filename)

  await browser.close()

async def run_page(page, config, data_row, screenshot_filename, **options):
  viewport_width = config.get("viewport_width", 800)
  viewport_height = config.get("viewport_height", 1200)

  await page.setViewport({ "width": viewport_width, "height": viewport_height})
  await page.goto(f"file:///{pathlib.Path().resolve()}/page_template.html")

  # Update background image.
  javascript = """
    dom = document.querySelector('#form-image');
    dom.setAttribute('src', '""" + config.get("image_file") + """');
  """
  await page.evaluate(javascript)

  # Adding font link in Head tag.
  font_option = random.choices(config.get("font_options", []))[0]
  font_tag = f'<link href="{font_option.get("font_link")}" rel="stylesheet">'
  font_size = font_option.get("font_size", 14)
  await prepend_text_to_tag(page, "head", font_tag)

  # Adding image width class to style tag.
  css_class = """
    .viewport {
      width: """ + str(viewport_width) + """px;
    }

    .custom-font {
      font-family: \\'""" + font_option.get("font_family") + """\\', serif;
      font-size: """ + str(font_size) + """;
    }
  """
  css_class = "\\n" + css_class.replace("\n", " ") + "\\n"
  await append_text_to_tag(page, "head > style", css_class)

  # Adding floating text tags to the end of Body tag.
  additional_tags = ""
  for field in config.get("fields", []):
    field_name = field.get("name", None)

    if "function" in field:
      data_value = get_function_field_value(field)
    else:
      data_value = data_row[field_name]

    # Extract sub value using regex.
    if "regex" in field:
      matches = re.match(field["regex"], data_value)
      if not matches:
        raise Exception(f"Unable to match value for {field_name} using regex: "
            + field["regex"])
      data_value = matches[field.get("regex_match_group", 1)]

    position_x = field.get("position_x", 0)
    position_y = field.get("position_y", 0)
    text_font_size = field.get("font_size", font_size)
    additional_tags += \
      f'<div class="float-text custom-font" \
        style="font-size: {text_font_size}px; top: {position_y}px; \
        left: {position_x}px;">{data_value}</div>'
  await append_text_to_tag(page, "body", additional_tags)

  # Sleep 1 seconds
  time.sleep(1)

  # Get screenshot of the page.
  await page.screenshot({"path": screenshot_filename})

async def append_text_to_tag(page, css_selector, text):
  javascript = """
    dom = document.querySelector('""" + css_selector + """');
    dom.innerHTML = dom.innerHTML + '""" + text + """';
  """
  await page.evaluate(javascript)

async def prepend_text_to_tag(page, css_selector, text):
  javascript = """
    dom = document.querySelector('""" + css_selector + """');
    dom.innerHTML = '""" + text + """' + dom.innerHTML;
  """
  await page.evaluate(javascript)

def get_function_field_value(field):
  field_function = field.get("function", None)

  if field_function == "today":
    return datetime.today().strftime('%Y-%m-%d')

  elif field_function == "text":
    return field.get("text")

  else:
    return ""

def generate_image(config, data_list, **options):
  asyncio.get_event_loop().run_until_complete(
    run_browser(config, data_list, **options))

def load_json_file(file_path):
  with open(file_path, "r", encoding="utf-8") as f:
    json_dict = json.load(f)
    return json_dict

def load_csv_file(file_path):
  with open(file_path, newline="") as f:
    data_list = [{k: v for k, v in row.items()}
      for row in csv.DictReader(f, skipinitialspace=True)]
    return data_list

def get_parser():
  # Read command line arguments
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      Script used to generate fake image forms with pre-generated data in CSV.
      """,
      epilog="""
      Examples:

      # Create images with pre-generated data and empty form image.
      python generate_images.py --config=path-to-config.json --data=path-to-data.csv --output-folder=.tmp/
      """)
  parser.add_argument(
      "--config",
      dest="config",
      help="Path to config JSON file")
  parser.add_argument(
      "--data",
      dest="data",
      help="Path to data CSV file")
  parser.add_argument(
      "--output-folder",
      dest="output_folder",
      help="Path to the destination output folder")
  parser.add_argument('--debug', dest='debug', action='store_true')

  return parser

if __name__ == "__main__":
  parser = get_parser()
  args = parser.parse_args()

  if not args.config or not args.output_folder or not args.data:
    parser.print_help()
    exit()

  options = {
    "output_folder": args.output_folder,
    "debug": args.debug,
  }

  config = load_json_file(args.config)
  data_list = load_csv_file(args.data)
  generate_image(config, data_list, **options)

  print(f"Wrote {len(data_list)} images to {args.output_folder}")
