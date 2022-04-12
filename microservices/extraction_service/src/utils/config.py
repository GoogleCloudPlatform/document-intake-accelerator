"""
This is Document and state mapping dict
Default entities sections have entities that are coming from parser
Derived section have information of entities which are not extracted from
parser and need to extract them by using pattern
Create state wise mapping if it form parser, and one doc type mapping
if it is specialized parser
"""
# Project name
PROJECT_NAME = "claims-processing-dev"
# Attributes not required from specialized parser raw json
NOT_REQUIRED_ATTRIBUTES_FROM_SPECIALIZED_PARSER_RESPONSE = ["textStyles",
                                                            "textChanges",
                                                            "revisions",
                                                            "pages.image"]
# GCS temp folder to store async form parser output
GCS_OP_URI = "gs://async_form_parser"
FORM_PARSER_OP_TEMP_FOLDER = "temp7"
MAPPING_DICT = {
  "unemployment_form_arizona": {
    "default_entities": {
      "Social Security Number:": ["Social Security Number"],
      "Date:": ["Date"],
      "Primary Phone: ": ["Employee Primary Phone"],
      "First Name": ["Employee First Name"],
      "Last Name": ["Employee Last Name"],
      "Mailing Address (No., Street, Apt., P.O. Box) ": [
        "Employee Mailing Address (No., Street, Apt., P.O.Box)"],
      "E-MAIL Address (Optional but Encouraged) ": [
        "Employee E-MAIL Address (Optional but Encouraged)"],
      "Gender": ["Employee Gender"],
      "Race": ["Employee Race"],
      "Ethnicity": ["Employee Ethnicity"],
      "Language": ["Employee Language"],
      "Mailing Address (No., Street, Apt., P.O. Box, City)": [
        "Employer Mailing Address (No., Street, Apt., P.O.Box, City)"],
      "Date": ["Date"],
      "City": ["Employee Residence City", "Employee City"],
      "State": ["Employee State", "Employee Residence State", "Employer State"],
      "Employer's Phone No.": ["Employer's Phone No."],
      "Claimant's Signature": ["Claimant's Signature"],
      "Company's Name ": ["Company's Name"],
      "ZIP": ["Employee Residence ZIP", "Employee ZIP", "Employer ZIP"],
      "Month": ["Employee DOB Month", "Month (Last Day of Work)"],
      "Day": ["Employee DOB Day", "Day (Last Day of Work)"],
      "Year": ["Employee DOB Year", "Year (Last Day of Work)"]
    }
  },

  "unemployment_form_california": {
    "default_entities": {
      "Name of issuing State/entity": ["Name of issuing Stata/entity"],
      "Driver License Number": ["Driver License Number"],
      "Race": ["Employee Race"],
      "Ethnicity": ["Employee Ethnicity"],
      "Language": ["Employee Language"],
      "22. Employer name": ["Longest Employer name"],
      "Months": ["Months worked for longest employer"]
    },
    "derived_entities":
      {
        "What is your birth date?": {
          "rule": "What is your birth date\?\n\d\.(.*?)\((mm/dd/yyyy)"},
        "What is your gender?": {
          "rule": "What is your gender\?\n\d\.(.*?)\n\d"},
        "Expiration Date (EXP)": {
          "rule": "\sAlien Registration Number \(A#\)\n3\)\s(\d{4}-\d{2}-\d{2})\n"}}
  },

  "unemployment_form_arkansas": {
    "default_entities": {
      "TODAY'S DATE": ["TODAY'S DATE"],
      "SOCIAL SECURITY NUMBER": ["SOCIAL SECURITY NUMBER"],
      "EFFECTIVE DATE: (Local Office Only)": [
        "EFFECTIVE DATE: (Local Office Only)"],
      "FIRST NAME": ["EMPLOYEE FIRST NAME"],
      "MIDDLE INITIAL": ["EMPLOYEE MIDDLE INITIAL"],
      "LAST NAME": ["EMPLOYEE LAST NAME"],
      "Mailing Address": ["EMPLOYEE Mailing Address"],
      "State of Residence": ["Employee State of Residence"],
      "County of Residence": ["Employee County of Residence"],
      "DATE OF BIRTH": ["EMPLOYEE DATE OF BIRTH"],
      "EMPLOYER NAME": ["EMPLOYER NAME"],
      "STREET NAME": ["EMPLOYER STREET NAME"],
      "COUNTY": ["EMPLOYER COUNTY"],
      "EMPLOYER PHONE": ["EMPLOYER PHONE"],
      "FIRST DATE WORKED AT YOUR LAST JOB": [
        "FIRST DATE WORKED AT YOUR LAST JOB"],
      "DATE LAST WORK ENDED": ["DATE LAST WORK ENDED"],
      "What kind of work did you do on your last job": [
        "What kind of work did you do on your last job?"],
      "Date": ["Date"],
      "Signature": ["Signature"],
      "E-Mail Address": ["Employee E-Mail Address"]
    }
  },

  "unemployment_form_illinois": {
    "default_entities": {
      "Claimant ID": ["Claimant ID"],
      "SSN": ["SSN"],
      "First Name": ["Employee First Name"],
      "MI": ["Employee MI"],
      "Last Name": ["Employee Last Name"],
      "Date of Birth: (mm/dd/yyyy)": ["Date of Birth: (mm/dd/yyyy)"],
      "E-Mail Address": ["Employee E-Mail Address"],
      "Driver's License Number": ["Driving Licence Number"],
      "Primary Telephone": ["Employee Mailing Primary Telephone"],
      "Employer Name": ["Employer Name"],
      "Expiration Date": ["Expiration Date"],
      "Document Type": ["Document Type"],
      "Gender": ["Employee Gender"],
      "Ethnicity": ["Employee Ethinicity"],
      "Company Phone": ["Company Phone"],
      "For this period of employment, what date did you start": [
        "For this period of employment, what date did you start?"],
      "Last date worked": ["Last date worked"],
      "CLAIMANT SIGNATURE": ["CLAIMANT SIGNATURE"],
      "DATE": ["DATE"]
    }
  },

  "claims_form_arizona": {
    "default_entities": {
      "Social Security Number": ["Social Security Number"],
      "Name": ["Employee Name"],
      "Week Ending Date": ["Week Ending Date"],
      "What were your gross earnings before deductions?": [
        "What were your gross earnings before deductions?"],
      "What was your last day of work?": ["What was your last day of work?"],
      "Claimant's Signature": ["Claimant's Signature "]
    },
    "table_entities": {

    }
  },

  "claims_form_arkansas": {
    "default_entities": {
      "SIGNATURE": ["SIGNATURE"],
      "NAME ": ["CLAIMANT NAME", "EMPLOYEE NAME"],
      "EMPLOYER NAME": ["EMPLOYER NAME"],
      "SSN": ["SSN"],
      "STREET OR BOX NO": ["EMPLOYEE STREET OR BOX NO.",
                           "EMPLOYER STREET OR BOX NO."],
      "CITY": ["EMPLOYEE CITY", "EMPLOYER CITY"],
      "STATE": ["EMPLOYEE STATE", "EMPLOYER STATE"],
      "ZIP CODE": ["EMPLOYEE ZIP CODE", "EMPLOYER ZIP CODE"],
      "LAST DAY WORKED ": ["LAST DAY WORK"],
      "PHONE NO": ["EMPLOYEE PHONE NO."],
      "DATE BEGAN WORK": ["DATE BEGAN WORK"],
      "EMPLOYER'S NAME AND ADDRESS": ["EMPLOYER'S NAME AND ADDRESS"]

    }
  },

  "utility_bill": {
    "default_entities": {
      "receiver_name": ["name"],
      "supplier_address": ["reciever address"],
      "due_date": ["due date"],
      "invoice_date": ["Invoice date"],
      "supplier_account_number": ["Account no"],
    }
  },

  "driving_licence": {
    "default_entities": {
      "Document Id": ["DLN"],
      "Expiration Date": ["EXP"],
      "Date Of Birth": ["DOB"],
      "Family Name": ["LN"],
      "Given Names": ["FN"],
      "Issue Date": ["ISS"],
      "Address": ["Address"],
    },
    "derived_entities": {"SEX": {"rule": "SEX.*?(?<!\w)(F|M)(?!\w)"}}
  },

  "pay_stub": {
    "default_entities": {
      "employee_address": ["EMPLOYER ADDRESS"],
      "employee_name": ["EMPLOYEE NAME"],
      "end_date": ["PAY PERIOD(TO)"],
      "gross_earnings_ytd": ["YTD Gross"],
      "pay_date": ["PAY DATE"],
      "ssn": ["SSN"],
      "start_date": ["PAY PERIOD(FROM)"]

    },
    "derived_entities":
      {"EMPLOYER NAME": {"rule": "([a-zA-Z ]*)\d*.*"},
       "RATE": {"rule": "Regular\n(.*?)\n"},
       "HOURS": {"rule": "Regular\n.*?\n(.*?)\n"}}
  }
}
