
PROJECT_NAME = "claims-processing-dev"

NOT_REQUIRED_ATTRIBUTES_FROM_SPECIALIZED_PARSER_RESPONSE = ["textStyles", "textChanges", "revisions",
                                                    "pages.image"]

GCS_OP_URI = "gs://async_form_parser"
FORM_PARSER_OP_TEMP_FOLDER = "temp"

MAPPING_DICT = {
   "arizona": {
        "default_entities": {
              "Social Security Number:" : ["Social Security Number"],
              "Date:\n": ["Date"],
              "Primary Phone: ": ["Employee Primary Phone"],
              "First Name\n": ["Employee First Name"],
              "Last Name\n": ["Employee Last Name"],
              "Mailing Address (No., Street, Apt., P.O. Box) ": ["Employee Mailing Address (No., Street, Apt., P.O.Box)"],
              "E-MAIL Address (Optional but Encouraged) ": ["Employee E-MAIL Address (Optional but Encouraged)"],
              "Gender\n": ["Employee Gender"],
              "Race\n": ["Employee Race"],
              "Ethnicity\n": ["Employee Ethnicity"],
              "Language\n": ["Employee Language"],
              "Mailing Address (No., Street, Apt., P.O. Box, City)\n": ["Employer Mailing Address (No., Street, Apt., P.O.Box, City)"],
              "Date\n": ["Date"],
              "City\n": ["Employee Residence City", "Employee City"],
              "State\n": ["Employee State", "Employee Residence State"],
              "State ": ["Employer State"],
              "Employer's Phone No.\n": ["Employer's Phone No."],
              "Claimant's Signature " : ["Claimant's Signature"],
              "Company's Name ": ["Company's Name"],
              "ZIP\n": ["Employee Residence ZIP", "Employee ZIP", "Employer ZIP"],
              "Month\n": ["Employee DOB Month", "Month (Last Day of Work)"],
              "Day ": ["Employee DOB Day", "Day (Last Day of Work)"],
              "Year\n": ["Employee DOB Year", "Year (Last Day of Work)"]
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



