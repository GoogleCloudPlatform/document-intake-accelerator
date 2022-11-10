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

from faker import Faker
from faker.providers.phone_number import Provider
from healthcare_provider import HealthcareProvider
import random
import csv
import json
from datetime import datetime
from datetime import date
import datetime
from datetime import timedelta
import argparse
import re
from dateutil.relativedelta import relativedelta

faker = None

def add_years(start_date, years):
    try:
        return start_date.replace(year=start_date.year + years)
    except ValueError:
        # 👇️ preseve calendar day (if Feb 29th doesn't exist, set to 28th)
        return start_date.replace(year=start_date.year + years, day=28)

class CustomPhoneNumberProvider(Provider):
    def custom_phone_number(self, country_code="+1", num_digits=9):
        # print(f'{country_code}{self.msisdn()[:num_digits]}', '************')
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

        elif faker_function == "address":
            field_value = faker.address()
            if field.get("exclude_po_box", True):
                while re.match(".*(\s|\n)+(FPO|DPO|APO) (AA|AP|AE).*", field_value):
                    field_value = faker.address()

        elif faker_function:
            field_value = eval(f"faker.{faker_function}({params_str})")

        elif derive_from:
            derive_regex = field.get("derive_regex", "")
            matches = re.match(
                derive_regex, row_data[derive_from], re.IGNORECASE)
            field_value = matches[field.get("derive_match_group", 1)]

        else:
            field_value = field["value"]

        # Make endDate with in an year of a startDate
        if field_name.startswith("startDate"):
            key = field_name[9:]
            endDateKey = "endDate"+key
            print(endDateKey)
            endDate = faker.date_between(field_value, add_years(field_value, 1))
            field_value = field_value.strftime(field["date_format"])
            row_data[endDateKey] = endDate.strftime(field["date_format"])

        # Convert date in string format.
        if isinstance(field_value, datetime.date) and "date_format" in field:
            field_value = field_value.strftime(field["date_format"])

        if field_name == "isUrgent":
            if field_value:
                field_value = "✔"
                row_data["isNonUrgent"] = " "
            else:
                field_value = " "
                row_data["isNonUrgent"] = "✔"
        
        if field_name == "isInitialRequest":
            if field_value:
                field_value = "✔"
                row_data["isNonInitialRequest"] = " "
            else:
                field_value = " "
                row_data["isNonInitialRequest"] = "✔" 
        
        if field_name == "gender":
            row_data["isGenderMale"] = " "
            row_data["isGenderFemale"] = " "
            row_data["isGenderOther"] = " "
            row_data["isGenderUnknown"] = " "
            if field_value == "male":
                row_data["isGenderMale"] = "✔"
            elif field_value == "female":
                row_data["isGenderFemale"] = "✔"
            elif field_value == "other":
                row_data["isGenderOther"] = "✔"
            elif field_value == "unknown":
                row_data["isGenderUnknown"] = "✔"

        if field_name == "procedureType":
            row_data["isInpatient"] = " "
            row_data["isOutpatient"] = " "
            row_data["isProviderOffice"] = " "
            row_data["isObservation"] = " "
            row_data["isHome"] = " "
            row_data["isDaySurgery"] = " "
            row_data["isProcTypeOther"] = " "
            row_data["otherProcType"] = " "
            if field_value == "Inpatient":
                row_data["isInpatient"] = "✔"
            elif field_value == "Outpatient":
                row_data["isOutpatient"] = "✔"
            elif field_value == "ProviderOffice":
                row_data["isProviderOffice"] = "✔"
            elif field_value == "Observation":
                row_data["isObservation"] = "✔"
            elif field_value == "Home":
                row_data["isHome"] = "✔"
            elif field_value == "DaySurgery":
                row_data["isDaySurgery"] = "✔"
            elif field_value == "Other":
                row_data["isProcTypeOther"] = "✔" 
                row_data["otherProcType"] = faker.pystr(10)   

        if field_name == "serviceType":
            row_data["isPhysicalTherapy"] = " "
            row_data["isOccupationalTherapy"] = " "
            row_data["isSpeechTherapy"] = " "
            row_data["isCardiacRehab"] = " "
            row_data["isMentalHealth"] = " "
            if field_value == "PhysicalTherapy":
                row_data["isPhysicalTherapy"] = "✔"
            elif field_value == "OccupationalTherapy":
                row_data["isOccupationalTherapy"] = "✔"
            elif field_value == "SpeechTherapy":
                row_data["isSpeechTherapy"] = "✔"
            elif field_value == "CardiacRehab":
                row_data["isCardiacRehab"] = "✔"
            elif field_value == "MentalHealth":
                row_data["isMentalHealth"] = "✔"

        if field_name == "isHomeHealth":
            row_data["hhMdSignedAttachedYes"] = " "
            row_data["hhMdSignedAttachedNo"] = " "
            row_data["hhRnAssmtAttachedYes"] = " "
            row_data["hhRnAssmtAttachedNo"] = " "
            row_data["hhQty"] = " "
            row_data["hhDuration"] = " "
            row_data["hhFrequency"] = " "
            row_data["hhOther"] = " "
            if field_value:
                field_value = "✔"
                
                mdSignedAttached = random.choice([True, False]) 
                if mdSignedAttached:
                    row_data["hhMdSignedAttachedYes"] = "✔"
                    row_data["hhMdSignedAttachedNo"] = " "
                else:
                    row_data["hhMdSignedAttachedYes"] = " "
                    row_data["hhMdSignedAttachedNo"] = "✔"
                
                rnSignedAttached = random.choice([True, False])
                if rnSignedAttached:
                    row_data["hhRnAssmtAttachedYes"] = "✔"
                    row_data["hhRnAssmtAttachedNo"] = " "
                else:
                    row_data["hhRnAssmtAttachedYes"] = " "
                    row_data["hhRnAssmtAttachedNo"] = "✔"
                
                row_data["hhQty"] = faker.hc_sessions()
                row_data["hhDuration"] = faker.hc_duration()
                row_data["hhFrequency"] = faker.hc_frequency()
                row_data["hhOther"] = faker.pystr(20)          
            else:
                field_value = " "

        if field_name == "isDME":
            row_data["dmeMdSignedAttachedYes"] = " "
            row_data["dmeMdSignedAttachedNo"] = " "
            row_data["dmeTitle19CertAttachedYes"] = " "
            row_data["dmeTitle19CertAttachedNo"] = " "
            row_data["dmeEquipment"] = " "
            row_data["dmeDuration"] = " "
            if field_value:
                field_value = "✔"
                
                mdSigned = random.choice([True, False]) 
                if mdSigned:
                    row_data["dmeMdSignedAttachedYes"] = "✔"
                    row_data["dmeMdSignedAttachedNo"] = " "
                else:
                    row_data["dmeMdSignedAttachedYes"] = " "
                    row_data["dmeMdSignedAttachedNo"] = "✔"
                
                title19CertAttached = random.choice([True, False]) 
                if title19CertAttached:
                    row_data["dmeTitle19CertAttachedYes"] = "✔"
                    row_data["dmeTitle19CertAttachedNo"] = " "
                else:
                    row_data["dmeTitle19CertAttachedYes"] = " "
                    row_data["dmeTitle19CertAttachedNo"] = "✔"
                
                row_data["dmeEquipment"] = faker.dme_equipment()
                row_data["dmeDuration"] = faker.hc_duration()         
            else:
                field_value = " "

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
        # if debug:   
        #     print(field_key, field_value)
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

    # print(f"Generating test data for {args.num_rows} rows...")
    config = load_json_file(args.config)

    faker = Faker(config.get("languages", ["en_US"]))
    faker.add_provider(CustomPhoneNumberProvider)
    faker.add_provider(HealthcareProvider)

    data = generate_data(config, args.num_rows, **options)
    write_to_csv(args.output, data)

    print(f"Wrote to file {args.output}")
