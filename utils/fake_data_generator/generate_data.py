from faker import Faker
from faker.providers.phone_number import Provider
import csv
import json
import datetime
import argparse
import re

faker = None

class CustomPhoneNumberProvider(Provider):
    def custom_phone_number(self, country_code="+1", num_digits=9):
        return f'{country_code}{self.msisdn()[:num_digits]}'


def generate_data_row(fields, **options):
  row_data = {}
  for field in fields:
    field_name = field["name"]
    faker_params = field.get("faker_params", {})
    faker_function = field.get("faker_function", None)
    derive_from = field.get("derive_from", None)
    debug = options.get("debug", False)

    param_list = []
    for key, value in faker_params.items():
      param_list.append(f"{key}={value}")
    params_str = ",".join(param_list)

    # Generate fake data if faker_function is defined. Otherwise, use the
    # default value.
    if faker_function == "phone_number":
      field_value = faker.custom_phone_number(
          country_code=str(field.get("country_code", "+1")),
          num_digits=field.get("num_digits", 9))

    elif faker_function:
      field_value = eval(f"faker.{faker_function}({params_str})")

    elif derive_from:
      derive_regex = field.get("derive_regex", "")
      matches = re.match(derive_regex, row_data[derive_from], re.IGNORECASE)
      field_value = matches[field.get("derive_match_group", 1)]

    else:
      field_value = field["value"]

    # Convert string format.
    if isinstance(field_value, datetime.date) and "date_format" in field:
      field_value = field_value.strftime(field["date_format"])

    if field.get("single_quotes", False):
      field_value = f"'{field_value}'"
    if field.get("double_quotes", False):
      field_value = f'"{field_value}"'

    row_data[field_name] = field_value

  if debug:
    print("Adding row:")
    print(row_data)

  # Convert all values to string and remove line breaks.
  for field_key in row_data.keys():
    field_value = str(field_value)
    field_value = " ".join(field_value.split())
    row_data[field_key] = row_data[field_key].replace("\n", " ")

  return row_data

def generate_data(config, num_rows, **options):
  fields = config.get("fields", [])
  data_list = []

  for i in range(num_rows):
    data_list.append(generate_data_row(fields, **options))

  return data_list

def write_to_csv(file_name, data_list):
  with open(file_name, "w", encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file)
    count = 0
    for row in data_list:
      if count == 0:
        header = row.keys()
        csv_writer.writerow(header)
        count += 1
      csv_writer.writerow(row.values())
  return file_name

def load_json_file(file_path):
  with open(file_path, "r", encoding="utf-8") as f:
    json_dict = json.load(f)
    return json_dict

def get_parser():
  # Read command line arguments
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      Script used to generate fake data and save to a CSV file.
      """,
      epilog="""
      Examples:

      # Create a csv file of 100 unique rows.
      python generate_data.py --config=path-to-config.json --output=sample.json --num-records=100
      """)
  parser.add_argument(
      "--config",
      dest="config",
      help="Path to config JSON file")
  parser.add_argument(
      "--output",
      dest="output",
      help="Path to the destination output CSV file")
  parser.add_argument(
      "--num-rows",
      dest="num_rows",
      type=int,
      default=100,
      help="Number of rows to be generated")
  parser.add_argument('--debug', dest='debug', action='store_true')

  return parser

if __name__ == "__main__":
  parser = get_parser()
  args = parser.parse_args()

  if not args.config or not args.output:
    parser.print_help()
    exit()

  options = {
    "debug": args.debug,
  }

  print(f"Generating test data for {args.num_rows} rows...")
  config = load_json_file(args.config)

  faker = Faker(config.get("languages", ["en_US"]))
  faker.add_provider(CustomPhoneNumberProvider)

  data = generate_data(config, args.num_rows, **options)
  write_to_csv(args.output, data)

  print(f"Wrote to file {args.output}")
