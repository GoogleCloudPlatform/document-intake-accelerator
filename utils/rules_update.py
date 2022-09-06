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

'''
This script is used for Updating the Validation Rules
'''

# Create the parser
import argparse
from sys import argv
import os
import json
from copy import deepcopy
from six import string_types
from jinjasql import JinjaSql
from google.cloud import storage
from commmon.utils.logging_handler import Logger
from common.config import PATH,BUCKET_NAME_VALIDATION,PATH_TEMPLATE,PROJECT_ID
file_name=PATH.rsplit('/', 1)[-1]


def parsers():
  '''
  Define the Various Command Line arguments as well as Flags available to the user

  Returns:
    args: Returns the command line arguments taken from the User
  '''
  parser = argparse.ArgumentParser()
  # Add an argument
  template_choices = ['Template1', 'Template2','Template3','Template4',
  'Template5','Template6']

  parser.add_argument('--template',type=str,
    choices=template_choices,
    help = "Select One of the available Templates",required=True)

  parser.add_argument('--key', type=str,
    required=(template_choices[1] not in argv
        and '-v' not in argv and '-d' not in argv),
    help="Enter the Key Name")

  parser.add_argument('--doc_type', type=str,
    required=True,
    help = "Enter the Document Name")

  parser.add_argument('--operator', type=str,
    required =((template_choices[2]) in argv) or (template_choices[3] in argv),
    help= "Enter one of the Operators")

  parser.add_argument('-d','--delete', action='store_true',
    help = "Please Enter the doc_type and the Rule_id you wish to remove")

  parser.add_argument('-v','--view', action='store_true',
    help = "Enter the doctype for which you wish to view the existing rules")

  parser.add_argument('--ruleid', type=str,
    required = '-d' in argv)

  parser.add_argument('--value', type=str,
    required=((template_choices[0] not in argv) and
        template_choices[1] not in argv and
        '-v' not in argv and '-d' not in argv) ,
    help = "Enter the Value to compare with the select operators")

  parser.add_argument('--value_before', type=int,
    required=(template_choices[0] in argv),
    help = "Months to subtract from the current date(Only for Template1)")

  parser.add_argument('--value_after', type=int,
    required=(template_choices[0] in argv),
    help="Value in months to add to the current date(Only for Template1)")

  parser.add_argument("--key_list", nargs="+",
    required=(template_choices[1] in argv),
    help = "Enter the keys.(Template 2 only)")

  parser.add_argument("--operator_list", nargs="+",
    required=(template_choices[1] in argv),
    help = "Enter the operators(Template 2 only)")

  parser.add_argument("--value_list", nargs="+",
    required=(template_choices[1] in argv),
    help = " Enter the values(Template 2 only)")

  args = parser.parse_args()
  return args


def read_json(path):
  """Function to read a json file directly from gcs
        Input: 
            path: gcs path of the json to be loaded
        Output:
            data_dict : dict consisting of the json output

  """
  bucket_name = path.split("/", 3)[2]
  file_path = path.split("/", 3)[3]
  client = storage.Client()
  bucket = client.get_bucket(bucket_name)
  blob = bucket.blob(file_path)
  data = blob.download_as_string(client=None)
  data_dict = json.loads(data)
  return data_dict


def get_params(args):
  '''
  Assign the Appropriate Parameters according to the input taken fron the Command Line
  Input :
    args:Command Line input taken from the User
  Output:
    params : Dictionary conisting of the necessary fields to plug into the SQL Query
  '''
  if args.delete:
    datak[args.doc_type].pop(args.ruleid)

  elif args.template == 'Template1':
    params={
    'key' : args.key,
    'BQ_Table' :"`project_table`",
    'doc_type' : args.doc_type,
    'value_before' : args.value_before,
    'value_after' : args.value_after}

  elif args.template == 'Template2':
    params = {
    'key' : args.key_list,
    'BQ_Table' : '`project_table`',
    'value' : args.value_list,
    'operator' : args.operator_list}
  else:
      params={
    'key' : args.key,
    'BQ_Table' :"`project_table`",
    'doc_type' : args.doc_type,
    'operator' : args.operator,
    'value' : args.value}

  return params


def check_float(potential_float):
  '''
  Check if the value passed to the function is a float or not
  '''
  try:
    float(potential_float)
    return True
  except ValueError:
    return False


def get_sql_from_template(query, bind_params):
  '''
  Get the Parameters Json and select the appropriate fields where single quote needs to be applied
  Input:
    query : Is the SQL Query prepared using teamplates
    bind_params : list of parameters
  Output:
    query%params : complete sql query with quotes added in appropriate location
  '''

  if not bind_params:
    return query
  params = deepcopy(bind_params)
  # Used for iterating on the key value dictionary
  for key, val in params.items():
    if "doc_type" in key or ("key" not in key and not check_float(val)):
      if "BQ_Table" in key:
        continue
      if "dim" in key:
        continue
      params[key] = quote_sql_string(val)
  return query % params


def quote_sql_string(value):
  '''
  If `value` is a string type, escapes single quotes in the string
  and returns the string enclosed in single quotes.
  '''
  if isinstance(value, string_types):
    if value in ['>','<','==','!=','=']:
      return value
    new_value = str(value)
    new_value = new_value.replace("'", "''")
    return "'{}'".format(new_value)
  return value


def prep_sql(template,params):
  '''
  Apply a JinjaSql template (string) substituting parameters (dict) and return
  the final SQL.
  Input:
    template : Template used for query Generation
    params: parameter dict to plug into the joinja template

  Output:
    jinn : the generated SQL Query
  '''
  j = JinjaSql(param_style='pyformat')
  query, bind_params = j.prepare_query(template, params)
  jinn = get_sql_from_template(query, bind_params)
  return jinn


def get_var(var):
  '''
  Used to Generate the Rule id for a new rule
  Input:
        var : Last Rule number of the currently existing rule list
  Output:
        rule_no : New Rule Number
  '''
  var = int(var.split('_')[1])
  rule_no = "Rule_" + str(var+1)
  return rule_no



def update_json(jinn,args):
  '''
  Add the newly create Sql Query(Rule) to the already existing Rules json
  Input:
    jinn: Newly Generated SQL Query(Rule)
    args" Command Line arguments recevied from the user
  Output:
    data : Updated Rule Dict
  '''
  try:
    data = read_json(PATH)
  except Exception:
    data={}
  rule_no = "Rule_1"
  try:
    get_list = list(data[args.doc_type].keys())
  except KeyError as e:
    data[args.doc_type]={rule_no : jinn}
    return data

  var=get_list[-1]
  if args.ruleid:
      rule_no = args.ruleid
  else:
      rule_no = get_var(var)
  if args.doc_type in data:
    data[args.doc_type][rule_no] = jinn
  return data



def load_template(data,args):
  '''
  As per the user input, the appropriate jinja template is loaded from the template file
  Input:
        data: dict consisting of the jinja templates
        args : Command Line input taken from the user
  Ouput:
        template : The Template selected as per the user input
  '''
  template = data[args.template]
  return template

def dump_updated_json(data):
  '''
  Update the newly created rules json
  Input:
        data: Dict with the updated rules included
  '''
  json.dump(data, open(file_name,"w"))



def upload_bucket():
  '''
  Upload the Newly Created json to the bucket
  '''

  n = 3
  groups = PATH.split('/')
  blob_name='/'.join(groups[n:])
  client = storage.Client(project=PROJECT_ID)
  bucket = client.get_bucket(BUCKET_NAME_VALIDATION)
  blob = bucket.blob(blob_name)
  blob.upload_from_filename(file_name)

def main():
  '''
  Main Function Used to control the code flow
  '''
  args=parsers()
  try:
    data = read_json(PATH_TEMPLATE)
  except FileNotFoundError:
    Logger.info(f"Template File Does not exist or the file path is incorrect")
    return
  if args.view:
    try:
      data = read_json(PATH)
    #Iterating on the rules to print one by one
      for i in data[args.doc_type]:
        Logger.info(f"{i} : {data[args.doc_type][i]}")
    except FileNotFoundError:
      Logger.info(f"File Does not exist or the file path is incorrect")
    except KeyError:
      Logger.info(f"Document Name is incorrect")
    return


  if args.delete:
    try:
      data = read_json(PATH)
      data[args.doc_type].pop(args.ruleid)
      json.dump(data, open(file_name,"w"))
      upload_bucket()
      os.remove(file_name)
    except FileNotFoundError:
      Logger.info(f"File Does not exist or the file path is incorrect")
    return
  params = get_params(args)
  template = load_template(data,args)
  try:
    jinn = prep_sql(template,params)
  except TypeError as e:
    Logger.info(f"Incorrect Input Format")
    return
  data = update_json(jinn,args)
  dump_updated_json(data)
  upload_bucket()
  os.remove(file_name)



if __name__ == "__main__":
  main()
