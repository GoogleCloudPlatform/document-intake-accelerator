''' Script to change json format'''
import json
from collections import ChainMap
'''
Input json format
json=[{
        "entity": "name",
        "value": "Kathr1n    marie",
        "key_confidence": 1.0,
        "value_confidence": 1.0
    },
    {
        "entity": "dob",
        "value": "2022-jan-09\n",
        "key_confidence": 1.0,
        "value_confidence": 1.0
    },
    {
        "entity": "phone_no",
        "value": "123A",
        "key_confidence": 1.0,
        "value_confidence": 1.0
    },
    {
        "entity": "address",
        "value": "XYZ",
        "key_confidence": 1.0,
        "value_confidence": 1.0
    },
   
    ]


'''

def get_json_format_for_processing(input_json):
    '''Function to change list of dictionary json format to key value mapping dictionary
    Input:
        input_json: input json with list of dictionary format
    Output:
        new_json: list of key value mapping dictionary'''
        
    a=input_json
    new_list=[]
    # for dictionary in input json
    for i in a:
        # get list of keys for the dictionary
        a={}
        #create a dictionary from input dictionary
        a[i.get("key")]=i.get("value")
        #append the new dictionary in a list
        new_list.append(a)
    res={}
    #convert list to dictionary
    res=dict(ChainMap(*new_list))
    #get new_json as list of dictionary
    new_json=[res]
    return new_json

def correct_json_format_for_db(output_dict,input_json):
    '''Function to add a list of dictionary for key value mapping
    to input list of dictionary json
    Input:
        output_dict: list of dictionary with key value mapping
        input_json: list of dictionary json
    Output:
        input_json: list of dictionary json'''
    #traverse input dictionary json
    for item in input_json:
        #traverse the keys in key value mapped dictionary
        for entity in output_dict[0].keys():
            #if keys are matched in both 
            if item.get("key")==entity:
                #reassign input json value to output dictionary velue
                item["value"]=output_dict[0][entity]
    return input_json


