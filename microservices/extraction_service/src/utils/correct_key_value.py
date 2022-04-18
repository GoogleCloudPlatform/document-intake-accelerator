
"""
This script is for postprocessing the extracted OCR output.
The configuration file for the script is post_processing_config.py
"""

import re
import datetime
from datetime import datetime
from .post_processing_config import str_to_num_dict, num_to_str_dict, \
  clean_value_dict, lower_to_upper_list, \
  upper_to_lower_list, clean_space_list, date_format_dict,\
  convert_to_string, convert_to_number
from common.utils.logging_handler import Logger

def list_to_string(string_list):
  '''Function to join a list of string characters to a single string
  Input:
   string_list: list of string characters
  Output:
   str1: concatenated string
  '''

  # initialize an empty string
  str1 = ''
  # traverse in the string
  str1=str1.join(string_list)
  # return string
  return str1


def string_to_number(value):
  ''' Function to correct a extracted integer value
  Input:
    value: Input string
  Output:
    value: Returns corrected string
  '''
  if value is None:
    pass
  else:
    # convert input string to list
    string = list(value)
    # traverse through the list
    for index, i in enumerate(string):
      # check for the match character in str_to_num template
      for k, v in str_to_num_dict.items():
        # check if upper case match
        if i == k:
          # check if input is in lower case
          if i.islower():
            # correct the value
            string[index] = v.lower()
          else:
            # check if input is in upper case
            # correct the value
            string[index] = v.upper()

    # concatenate list to string
    value = list_to_string(string)
  return value


def number_to_string(value):
  '''Function to correct a extracted string value
    Input:
     value: Input string
    Output:
     value: Returns corrected string
  '''
  if value is None:
    pass
  else:
    # convert input string to list
    string = list(value)

    # traverse through the list
    for index, i in enumerate(string):
      # check for the match character in num_to_str template
      for k, v in num_to_str_dict.items():
        # check if the key values match
        if i == k:
          # check if input string is in lower case
          if i.islower():
            # correct the value
            string[index] = v.lower()
          else:
            # check if input string is in upper case
            # correct the value
            string[index] = v.upper()
    # concatenate list to string
    value = list_to_string(string)
  return value


def upper_to_lower(value):
  '''Function to convert to lower case
    Input:
      value: Input string
    Output:
      corrected_value: converted string
  '''
  if value is None:
    corrected_value=value
  else:
    # convert to lower case
    corrected_value = value.lower()
  return corrected_value


def lower_to_upper(value):
  '''Function to convert to upper case
    Input:
      value: Input string
    Output:
      corrected_value: converted string
  '''
  if value is None:
    corrected_value=value
  else:
    # convert to upper case
    corrected_value = value.upper()
  return corrected_value

def clean_value(value, noise):
  '''Function to clean a extracted value
   Input:
     value: Input string
       noise: Noise in the input string
    Output:
       corrected_value: corrected string without noise
  '''
  if value is None:
    corrected_value=value
  else:
    # replace noise in string
    corrected_value = value.replace(noise, "")
  return corrected_value


def clean_multiple_space(value):
  '''Function to remove extra spaces in extracted value
  Input:
    value: Input string
  Output:
    corrected_value: corrected string removing extra spaces
  '''
  if value is None:
    corrected_value=value
  else:
    # create a pattern for extra space
    pattern = re.compile(r'\s{2,}')
    # replace the pattern with single space in the string
    corrected_value = re.sub(pattern, " ", value)
  return corrected_value


def get_date_in_format(input_date_format, output_date_format, value):
  '''Function to change a date format
    Input:
     input_date_format: input format of date
     output_date_format: output format of date
     value: Input date string
    Output:
      new_date: date in new format
  '''
  if value is None:
    new_date=value
  else:
    try:
      # convert existing date to new date format
      new_date = datetime.strptime(value, input_date_format)\
          .strftime(output_date_format)  # 2022-02-02
    except ValueError as e:
      # if any error in date format no change in input date
      new_date = value
      Logger.error(e)
  return new_date

def correction_script(corrected_dict, template):
  '''Function for correction of extracted values
    Input:
      corrected_dict:input dictionary with key value pair
      template: type of correction requested
    Output:
    corrected_dict: output dictionary with key and corrected value
  '''
  # traverse through the input dictionary
  for k, v in corrected_dict.items():
    # check for template type
    if template == "clean_value":
      # check for keys in template
      for key,noise in clean_value_dict.items():
        # if keys are matched
        if k == key:
          # get the noise from the template for that key
          noise = clean_value_dict.get(key)
          # copy input value
          input_value = v
          # iterate th
          for i in noise:
            # call clean_value function
            corrected_value = clean_value(input_value, i)
            input_value = corrected_value
            # modify the input dictionary to the corrected value
          corrected_dict[k] = corrected_value

    # check for template type
    if template == "lower_to_upper":
      # check for keys in template
      for item in lower_to_upper_list:
        # if keys are matched
        if k == item:
          # call lower_to_upper function
          corrected_value = lower_to_upper(v)
          # modify the input dictionary to the corrected value
          corrected_dict[k] = corrected_value

    # check for template type
    if template == "upper_to_lower":
      # check for keys in template
      for item in upper_to_lower_list:
        # if keys are matched
        if k == item:
          # call upper_to_lower function
          corrected_value = upper_to_lower(v)
          # modify the input dictionary to the corrected value
          corrected_dict[k] = corrected_value

    # check for template type
    if template == "clean_multiple_space":
      # check for keys in template
      for item in clean_space_list:
        # if keys are matched
        if k == item:
          # call clean_multiple_space function
          corrected_value = clean_multiple_space(v)
          # modify the input dictionary to the corrected value
          corrected_dict[k] = corrected_value

    # check for template type
    if template == "date_format":
      # check for keys in template
      for key,value in date_format_dict.items():
        # if keys are matched
        if k == key:
          # get key values from template
          value = date_format_dict.get(key)
          # call get_date_in_format function; value[0]=input date format;
          # value[1]=output date format
          corrected_value = get_date_in_format(value[0], value[1], v)
          # modify the input dictionary to the corrected value
          corrected_dict[k] = corrected_value

    # check for template type
    if template == "convert_to_string":
      # check for keys in template
      for item in convert_to_string:
        # if keys are matched
        if k == item:
          # call number_to_string function
          corrected_value = number_to_string(v)
          # modify the input dictionary to the corrected value
          corrected_dict[k] = corrected_value

    # check for template type
    if template == "convert_to_number":
      # check for keys in template
      for item in convert_to_number:
        # if keys are matched
        if k == item:
          # call string_to_number function
          corrected_value = string_to_number(v)
          # modify the input dictionary to the corrected value
          corrected_dict[k] = corrected_value
  # return corrected_dict
  return corrected_dict


def data_transformation(input_dict):
  '''
    Function for data transformation
    Input:
        input_dict: input dictionary of extraction
    Output:
        input_dict: original dictionary
        temp_dict: corrected dictionary
  '''
  try:
    # get a copy of input dictionary
    temp_dict = input_dict.copy()
    # traverse through input_dict
    for index, input_item in enumerate(input_dict):
      # get input dictionary
      corrected_dict = input_item.copy()
      # check for string
      corrected_dict = correction_script(corrected_dict, "convert_to_string")
      # check for number
      corrected_dict = correction_script(corrected_dict, "convert_to_number")
      # check for noise
      corrected_dict = correction_script(corrected_dict, "clean_value")
      # check for upper to lower
      corrected_dict = correction_script(corrected_dict, "upper_to_lower")
      # check for lower to upper
      corrected_dict = correction_script(corrected_dict, "lower_to_upper")
      # check for multiple spaces
      corrected_dict = correction_script(corrected_dict, "clean_multiple_space")
      # check for date format
      corrected_dict = correction_script(corrected_dict, "date_format")
      # correct input dictionary
      temp_dict[index] = corrected_dict
    return input_dict, temp_dict
  except ValueError as e:
    Logger.error(e)
    return None,None

# Function call
# input_dict=get_json_format_for_processing(input_json)
# input_dict,output_dict=data_transformation(input_dict)
# corrected_json=correct_json_format_for_db(output_dict,input_json)
