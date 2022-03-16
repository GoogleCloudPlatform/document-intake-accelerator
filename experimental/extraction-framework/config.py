
# Project name
PROJECT_NAME = "claims-processing-dev"

# Attributes not required from specialized parser raw json
NOT_REQUIRED_ATTRIBUTES_FROM_SPECIALIZED_PARSER_RESPONSE = ["textStyles", "textChanges", "revisions",
                                                    "pages.image"]

# GCS temp folder to store async form parser output
GCS_OP_URI = "gs://async_form_parser"
FORM_PARSER_OP_TEMP_FOLDER = "temp"

# Document and state mapping dict
MAPPING_DICT = {
   "arizona": {
        "default_entities": {
              "Social Security Number:" : ["Social Security Number"],
              "Date:": ["Date"],
              "Primary Phone: ": ["Employee Primary Phone"],
              "First Name": ["Employee First Name"],
              "Last Name": ["Employee Last Name"],
              "Mailing Address (No., Street, Apt., P.O. Box) ": ["Employee Mailing Address (No., Street, Apt., P.O.Box)"],
              "E-MAIL Address (Optional but Encouraged) ": ["Employee E-MAIL Address (Optional but Encouraged)"],
              "Gender": ["Employee Gender"],
              "Race": ["Employee Race"],
              "Ethnicity": ["Employee Ethnicity"],
              "Language": ["Employee Language"],
              "Mailing Address (No., Street, Apt., P.O. Box, City)": ["Employer Mailing Address (No., Street, Apt., P.O.Box, City)"],
              "Date": ["Date"],
              "City": ["Employee Residence City", "Employee City"],
              "State": ["Employee State", "Employee Residence State"],
              "State": ["Employer State"],
              "Employer's Phone No.": ["Employer's Phone No."],
              "Claimant's Signature" : ["Claimant's Signature"],
              "Company's Name ": ["Company's Name"],
              "ZIP": ["Employee Residence ZIP", "Employee ZIP", "Employer ZIP"],
              "Month": ["Employee DOB Month", "Month (Last Day of Work)"],
              "Day": ["Employee DOB Day", "Day (Last Day of Work)"],
              "Year": ["Employee DOB Year", "Year (Last Day of Work)"]
              }
   },
    "arkansas": {
        "default_entities": {
            "TODAY'S DATE": ["TODAY'S DATE"],
            "SOCIAL SECURITY NUMBER": ["SOCIAL SECURITY NUMBER"],
            "EFFECTIVE DATE: (Local Office Only)": ["EFFECTIVE DATE: (Local Office Only)"],
            "FIRST NAME": ["EMPLOYEE FIRST NAME"],
            "MIDDLE INITIAL": ["EMPLOYEE MIDDLE INITIAL"],
            "LAST NAME": ["EMPLOYEE LAST NAME"],
            "Mailing Address": ["EMPLOYEE Mailing Address"],
            "ZIP CODE": ["EMPLOYER ZIP CODE", "Current zip", "EMPLOYEE ZIP CODE"],
            "CITY": ["EMPLOYER CITY"],
            "State of Residence": ["Employee State of Residence"],
            "County of Residence": ["Employee County of Residence"],
            "DATE OF BIRTH": ["EMPLOYEE DATE OF BIRTH"],
            "EMPLOYER NAME": ["EMPLOYER NAME"],
            "STREET NAME": ["EMPLOYER STREET NAME"],
            "STATE": ["EMPLOYER STATE"],
            "COUNTY": ["EMPLOYER COUNTY"],
            "EMPLOYER PHONE": ["EMPLOYER PHONE"],
            "FIRST DATE WORKED AT YOUR LAST JOB": ["FIRST DATE WORKED AT YOUR LAST JOB"],
            "DATE LAST WORK ENDED": ["DATE LAST WORK ENDED"],
            "What kind of work did you do on your last job": ["What kind of work did you do on your last job?"],
            "Signature": ["Signature"],
            "Date": ["Date"]
        }
    },
   "driver_license": {
          "default_entities":{
                        "Document Id" : ["DLN"],
                        "Expiration Date": ["EXP"],
                        "Date Of Birth": ["DOB"],
                        "Family Name": ["LN"],
                        "Given Names": ["FN"],
                        "Issue Date": ["ISS"],
                        "Address": ["Address"],
                        },
          "derived_entities": {"SEX": {"rule": "SEX.*?(?<!\w)(F|M)(?!\w)"}}
   }
}



