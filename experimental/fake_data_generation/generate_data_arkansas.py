from faker import Faker
from faker.providers.phone_number import Provider
from random import randint  
import random
import string
import csv
import json
from datetime import datetime
from datetime import date
from datetime import timedelta
import datetime
import argparse
import re
from dateutil.relativedelta import relativedelta

faker = None

class CustomPhoneNumberProvider(Provider):
    def custom_phone_number(self, country_code="+1", num_digits=9):
        print(f'{country_code}{self.msisdn()[:num_digits]}','************')
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

    if faker_function == "claimant_id":
      field_value = randint(100,1000) 
          #num_digits=field.get("num_digits", 3))

    elif faker_function == "address":
      field_value = faker.address()
      if field.get("exclude_po_box", True):
        while re.match(".*(\s|\n)+(FPO|DPO|APO) (AA|AP|AE).*", field_value):
          field_value = faker.address()

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
  # generate fake data
  cities={1:['White Hall',71602,'Jefferson'],2:['Banks',71631,'Bradley'],3:['Crossett',71635,'Ashley'],4:['Dermott',71638,'Chicot'],5:['Dumas',71639,'Desha'],6:['Grady',71644,'Lincoln'],7:['Kingsland',71652,'Cleveland'],8:['Monticello',71655,'Drew'],9:['Star City',71667,'Lincoln'],10:['Bluff City',71722,'Nevada']}
  races={1:['hispanic or latino','white','spanish'],2:['hispanic or latino','white','mexican'],3:['none','white','english'],4:['none','african-american','english'],5:['none','asian','english'],6:['none','asian','hindi'],7:['none','asian','mandarin']}
  for i in data_list:
    i['claimant_id']= randint(1, 100) 
    vl=randint(1,10)
    vl1=randint(1,7)
    i['city']= cities[vl][0]
    i['zip_code']=cities[vl][1]
    i['county']=cities[vl][2]
    i['ethnicity']=races[vl1][0]
    i['race']=races[vl1][1]
    i['language']=races[vl1][2]
    i['state']= "Arkansas"
    i['document_type']='Unemployment Form'
    i['alien_registration_number']=randint(1000000,10000000000)
    i['MI']=i['middle_name'][0]
    # rate per month
    rate=[30,32,34,35] 
    # hours worked in 4 weeks
    hour= [160,180] 
    i['rate']=random.choice(rate)
    i['hour']=random.choice(hour)
    i['current_total']= i['rate'] * i['hour']
    i['current_deduct']=round(random.uniform(200,300),2)
    # cost post deduction
    i['net_total']=i['current_total']- i['current_deduct'] 
    i['ytd_gross']=round(random.uniform(19200,25200),2)
    i['ytd_deduct']=round(random.uniform(1000,1200),2)
    i['ytd_net']=i['ytd_gross']-i['ytd_deduct']
    day=[5,7,10]
    month=[1,2,3]
    month1=[15,12,10]
    i['today_date']=date.today()
    i['eff_date']=datetime.datetime.strptime(str(i['today_date']), "%Y-%m-%d").date()+relativedelta(days=random.choice(day))
    # employment end date
    i['work_end_date']=datetime.datetime.strptime(str(i['today_date']), "%Y-%m-%d").date()-relativedelta(months=random.choice(month))
    # employment start date
    i['work_start_date']=datetime.datetime.strptime(str(i['work_end_date']), "%Y-%m-%d").date()-relativedelta(months=random.choice(month1)) 
    i['last_day_of_prev_month'] =datetime.datetime.strptime(str(i['work_end_date']), "%Y-%m-%d").date().replace(day=1) - relativedelta(days=1) 
    i['start_day_of_prev_month'] = datetime.datetime.strptime(str(i['work_end_date']), "%Y-%m-%d").date().replace(day=1)- timedelta(days=i['last_day_of_prev_month'].day)
    i['payment_date'] =datetime.datetime.strptime(str(i['last_day_of_prev_month']), "%Y-%m-%d").date() + relativedelta(days=1)
    last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
    i['statement_date'] = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day) 
    i['due_date']=datetime.datetime.strptime(str(i['statement_date']), "%Y-%m-%d").date()+relativedelta(days=20) 
    ch=random.choice(string.ascii_letters)
    dl=str(randint(1000000,100000000))
    i['driver_license']=ch.upper() + '-' + dl
    gender=['F','M']
    i['gender']=random.choice(gender)
    start_date = datetime.date(2015, 1, 1)
    end_date = datetime.date(2021, 1, 1)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    i['license_iss_date']= start_date + datetime.timedelta(days=random_number_of_days)
    i['license_end_date']=i['license_iss_date'].replace(i['license_iss_date'].year + 5)
    dcl=['A','B','M','C','D']
    i['class']=random.choice(dcl)
    i['rest']='NONE'
    i['wt']=str(randint(99,220))+'lb'
    ht=round(random.uniform(4.5,6.5),2)
    i['ht']=str(ht)+'ft'
    i['dd']=''.join(random.choice('0123456789ABCDEF') for i in range(16))
    i['end']='NONE'
    colour=['BRW','BLK','BLUE','GRN']
    c1=['BRW','BLK']
    i['eyes']=random.choice(colour)
    i['hair']=random.choice(c1)
    number= randint(1000000000,10000000000)
    i['account_no']=str(number)+ '-' + str(randint(1,10))
    i['employee_id']=randint(10000,100000)
    i['check_no']=randint(10000,100000)
    
    
  print(data_list)
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
