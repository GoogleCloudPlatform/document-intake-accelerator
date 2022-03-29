# Project name
PROJECT_NAME = "claims-processing-dev"

# Attributes not required from specialized parser raw json
NOT_REQUIRED_ATTRIBUTES_FROM_SPECIALIZED_PARSER_RESPONSE = ["textStyles", "textChanges", "revisions",
                                                            "pages.image"]

# GCS temp folder to store async form parser output
GCS_OP_URI = "gs://async_form_parser"
FORM_PARSER_OP_TEMP_FOLDER = "temp"

"""

This is Document and state mapping dict
Default entities sections have entities that are coming from parser
Derived section have information of entities which are not extracted from parser and need to extract them by using pattern
Create state wise mapping if it form parser, and one doc type mapping if it is specialized parser

"""

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
            "State": ["Employee State", "Employee Residence State"],
            "State": ["Employer State"],
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
            "Middle Initial": ["Employee Middle Initial"],
            "Name of issuing State/entity": ["Name of issuing Stata/entity"],
            "Driver License Number": ["Driver License Number"],
            "Race": ["Employee Race"],
            "Ethnicity": ["Employee Ethnicity"],
            "Language": ["Employee Language"],
            "Name": ["Last Employer Name"],
            "From": ["First day of work (From)"],
            "To": ["Last Day of work (To)"],
            "Total Wages": ["Total Wages"],
            "d) How were you paid? (e.g., weekly, monthly, etc": ["How were you paid? (e.g., weekly, monthly, etc.?)"],
            "f) How many hours did you work per week": ["How many hours did you work per week?"],
            "22. Employer name": ["Longest Employer name"],
            "Years": ["Years worked for longest employer"],
            "Months": ["Months worked for longest employer"]
        }
    },

    "unemployment_form_arkansas": {
        "default_entities": {
            "TODAY'S DATE": ["TODAY'S DATE"],
            "SOCIAL SECURITY NUMBER": ["SOCIAL SECURITY NUMBER"],
            "EFFECTIVE DATE: (Local Office Only)": ["EFFECTIVE DATE: (Local Office Only)"],
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
            "FIRST DATE WORKED AT YOUR LAST JOB": ["FIRST DATE WORKED AT YOUR LAST JOB"],
            "DATE LAST WORK ENDED": ["DATE LAST WORK ENDED"],
            "What kind of work did you do on your last job": ["What kind of work did you do on your last job?"],
            "Date": ["Date"],
            "Signature": ["Signature"],
            "E-Mail Address": ["Employee E-Mail Address"]
        }
    },
    "driver_license": {
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
    "payslip": {
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
