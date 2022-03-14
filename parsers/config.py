
PROJECT_NAME = "claims-processing-dev"

NOT_REQUIRED_ATTRIBUTES_FROM_SPECIALIZED_PARSER_RESPONSE = ["textStyles", "textChanges", "revisions",
                                                    "pages.image"]

GCS_OP_URI = "gs://async_form_parser"
FORM_PARSER_OP_TEMP_FOLDER = "temp"

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



