''' This file is user editable'''
''' keys denote --> document type'''
# which a user has to pass as a 3rd argument in the 
'''match_json.py module.'''
# to find the matching score between the two JSON.
# "match_json.py" will use only the entities listed under a document type
# for matching score calculation.

# The values under each key are mapped to the values mentioned in "Entity Standardization" file
'''https://docs.google.com/spreadsheets/d/1vPHqtx6tZjcT8u2bqp-XqD3GGYeQ3Qge44jC_OYzytw/edit#gid=0'''
# 'COLUMN C' as it is supposed that the values of each key match with the key of the 
# input json file.

'''DOB format: yyyy/mm/dd'''


# Outer key is the doc type and inner keys signifies the keys or the entities that needs to be matched with the
# entities of the application doc. Inner keys must be weighted and their total weightage must be equal to 1

# DATES to be provided with their format used in the document
MATCHING_USER_KEYS_SUPPORTING_DOC = {
    "drivers_license": {
        'name': 0.16, 'dob': (0.16,'yyyy/mm/dd'), 'sex':0.16, 'dl_no':0.16, 'last_name':0.16, 'first_name':0.16},
    "utility_bill": {
        'name':0.50, 'address':0.50},
    "pay_stub": {
        'employee_name': 0.14, 'ytd': 0.14, 'rate': 0.14, 'hours': 0.14, 'pay_period_from': (0.14, 'yyyy/mm/dd'),
        'pay_period_to': (0.14, 'yyyy/mm/dd'), 'ssn': 0.14},  
    
 }
APPLICATION_DOC_DATE_FORMAT = 'yyyy/mm/dd'