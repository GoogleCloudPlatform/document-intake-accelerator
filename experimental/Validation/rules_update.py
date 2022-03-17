import argparse
# Create the parser
from sys import argv
import os
import json
from copy import deepcopy
from six import string_types
from jinjasql import JinjaSql
from google.cloud import storage

def parser():
  '''
  Define the Various Command Line arguments as well as Flags available to the user

  Returns:
    args: Returns the command line arguments taken from the User
  '''
  parser = argparse.ArgumentParser()
  # Add an argument
  template_choices = ['Template1', 'Template2','Template3','Template4','Template5','Template6']
  parser.add_argument('--template',type=str,choices=template_choices,help = "Select One of the available Templates")
  parser.add_argument('--key', type=str, required=(template_choices[1] not in argv and '-v' not in argv and '-d' not in argv), help="Enter the Key Name")
  parser.add_argument('--doc_type', type=str, required=True, help = "Enter the Document Name")
  parser.add_argument('--operator', type=str,required = ((template_choices[2]) in argv) or (template_choices[3] in argv),help= "Enter one of the Operators")
  # parser.add_argument('--value', type=str, required=((template_choices[0]) not in argv or 'Template2' not in argv),help = "Enter the Value over which you want to write the select operators")

  parser.add_argument('-d','--delete', action='store_true',help = "Please Enter the doc_type and Rule_id of the rule you wish to remove")
  parser.add_argument('-v','--view', action='store_true',help = "Enter the doctype for which you wish to view the existing rules")

  parser.add_argument('--ruleid', type=str,required = '-d' in argv)
  parser.add_argument('--value', type=str, required=((template_choices[0] not in argv) and template_choices[1] not in argv and '-v' not in argv and '-d' not in argv) , help = "Enter the Value over which you want to write the select operators")
  parser.add_argument('--value_before', type=int, required=(template_choices[0] in argv),help = "Value in months to subtract from the current date(Only for Template1)")
  parser.add_argument('--value_after', type=int, required=(template_choices[0] in argv),help="Value in months to add to the current date(Only for Template1)")
  parser.add_argument("--key_list", nargs="+",required=(template_choices[1] in argv),help = "To be used for multiple and conditions. Enter the keys over which you wish to write the conditions.(Template 2 only)")
  parser.add_argument("--operator_list", nargs="+",required=(template_choices[1] in argv),help = "To be used for multiple and conditions. Enter the operators over which you wish to write the conditions.(Template 2 only)")
  parser.add_argument("--value_list", nargs="+",required=(template_choices[1] in argv),help = "To be used for multiple and conditions. Enter the values over which you wish to write the conditions.(Template 2 only)")

  # parser.add_argument('--value',type=str, required=(template_choices[1] in argv))
  args = parser.parse_args()
  return args


def read_json(path):
  """Function to read a json file directly from gcs"""
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
    print("Hello")
    datak[args.doc_type].pop(args.ruleid)

  elif args.template == 'Template1':
    params={
    'key' : args.key,
    'BQ_Table' :"`claims-processing-dev.data_extraction.testing_json`",
    'doc_type' : args.doc_type,
    'value_before' : args.value_before,
    'value_after' : args.value_after}

  elif args.template == 'Template2':
    params = {
    'key' : args.key_list,
    'BQ_Table' : '`claims-processing-dev.data_extraction.testing_json`',   
    'value' : args.value_list,
    'operator' : args.operator_list}
  else:
      params={
    'key' : args.key,
    'BQ_Table' :"`claims-processing-dev.data_extraction.testing_json`",
    'doc_type' : args.doc_type,
    'operator' : args.operator,
    'value' : args.value}

  return params


def check_float(potential_float):
  '''
  Check if the value passed to the 
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

  for key, val in params.items():
    # print(key,val)
    if "doc_type" in key or ("key" not in key and not check_float(val)):
      if "BQ_Table" in key:
        continue
      if "dim" in key:
        continue
      # print("hah")
      print(key,val)
      params[key] = quote_sql_string(val)
  return query % params


def quote_sql_string(value):
  '''
  If `value` is a string type, escapes single quotes in the string
  and returns the string enclosed in single quotes.
  '''
  if isinstance(value, string_types):
    # print(value)
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
  # print(query % bind_params)
  # print(get_sql_from_template(query, bind_params))    
  jinn = get_sql_from_template(query, bind_params)
  return jinn


def get_var(var):
  '''
  Used to Generate the Rule id for a new rule
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
    data = read_json("gs://async_form_parser/Jsons/rules.json")
    rule_no = "Rule_1"
    try:
      get_list = list(data[args.doc_type].keys())
    except KeyError as e:
      print(e)
      data[args.doc_type]={rule_no : jinn}
      print(data)
      return data
    
    var=get_list[-1]
    if args.ruleid:
        rule_no = args.ruleid
    else:
        rule_no = get_var(var)
    if args.doc_type in data:
      data[args.doc_type][rule_no] = jinn
    return data
 
def load_json(filename):
  '''
  Given the file path, the json is loaded a dict variable and returned 
  '''
  file=open(filename)
  data= json.load(file) 
  return data


def load_template(data,args):
  '''
  As per the user input, the appropriate jinja template is loaded from the template file
  '''
  template = data[args.template]
  return template

def dump_updated_json(data):
  '''
  Update the newly created rules json
  '''
  json.dump(data, open("rules.json","w"))


  
def upload_bucket():
  '''
  Upload the Newly Created json to the bucket
  '''
  client = storage.Client(project='claims-processing-dev')
  bucket = client.get_bucket('async_form_parser')
  blob = bucket.blob('Jsons/rules.json')
  blob.upload_from_filename('rules.json')

def main():
  '''
  Main Function Used to control the code flows
  '''
  args=parser()
  # data = load_json('temp1.json')
  data = read_json("gs://async_form_parser/Jsons/temp1.json")
  if args.view:
    data = read_json("gs://async_form_parser/Jsons/rules.json")
    print(len(args.doc_type))
    for i in data[args.doc_type]:
      print(i,':',data[args.doc_type][i])
    return


  if args.delete:
    data = read_json("gs://async_form_parser/Jsons/rules.json")
    data[args.doc_type].pop(args.ruleid)
    json.dump(data, open("rules.json","w"))
    upload_bucket()
    os.remove("rules.json")
    print("Rule Deletion Succesfully")
    return
  params = get_params(args)
  template = load_template(data,args)
  try:
    jinn = prep_sql(template,params)
  except TypeError as e:
    print("Incorrect Input Format")
    return
  print(jinn)
  data = update_json(jinn,args)
  dump_updated_json(data)
  upload_bucket()
  os.remove("rules.json")

  print("Rules Updated Succesfully")    
   

if __name__ == "__main__":
  main()
