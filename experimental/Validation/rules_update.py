import argparse
# Create the parser
from sys import argv
import os
import json
from copy import deepcopy
from six import string_types
from jinjasql import JinjaSql

def parser():
    '''
    Define the Various Command Line arguments as well as Flags available to the user
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


def get_params(args):
    '''
    Assign the Appropriate Parameters according to the input taken fron the Command Line
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
    # print(params)

    return params
def strip_blank_lines(text):
    '''
    Removes blank lines from the text, including those containing only spaces.
    '''
    return os.linesep.join([s for s in text.splitlines() if s.strip()])


def check_float(potential_float):
    try:
        float(potential_float)
        return True
    except ValueError:
        return False


def get_sql_from_template(query, bind_params):
    '''
    Get the Parameters Json and select the appropriate fields where single quote needs to be applied
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
    '''
    j = JinjaSql(param_style='pyformat')
    query, bind_params = j.prepare_query(template, params)
    # print(query % bind_params)
    # print(get_sql_from_template(query, bind_params))    
    jinn = get_sql_from_template(query, bind_params)
    return jinn

def generate_id(data):
    get_list = list(data[args.doc_type].keys())
    var_last = get_list[-1]
    var_last = int(var_last.split('_')[1])

def get_var(var):
    var = int(var.split('_')[1])
    rule_no = "Rule_" + str(var+1)
    return rule_no



def update_json(jinn,args):
        '''
        Add the newly create Sql Query(Rule) to the already existing Rules json
        '''
        data = load_json('test.json')
        # print("Hehe")
        # print(len(data[args.doc_type]))
        # print(type(data))
        rule_no = "Rule_1"
        try:
            get_list = list(data[args.doc_type].keys())
        except KeyError as e:
            print(e)
            data[args.doc_type]={rule_no : jinn}
            print(data)
            return data
            # data[args.doc_type][rule_no] = jinn 
            # print("Document Name is Incorrect")
            # return

        # print(data)
        var=get_list[-1]
        # print(var)
        if args.ruleid:
                rule_no = args.ruleid
                # print(rule_no)
        else:
            # while rule_no in get_list:
                # print(var)
                rule_no = get_var(var)
            # print(rule_no)
        # var =int((sorted(data[args.doc_type].keys())[-1][-1:]))
        # var =(sorted(data[args.doc_type].keys())[-1])
        # var= int(var.split('_')[1])
        # print(var)
        # rule_no = "Rule_" + str(var+1)
        if args.doc_type in data:
            data[args.doc_type][rule_no] = jinn
        # print(data)
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
    json.dump(data, open("test.json","w"))


def main():
    args=parser()
    data = load_json('temp1.json')
    if args.view:
        data = load_json('test.json')
        # print(data)
        print(len(args.doc_type))
        for i in data[args.doc_type]:
            # for j in i:
            #     print(j)
            print(i,':',data[args.doc_type][i])
        return
            # print(data[i])
            # print("/n")

    if args.delete:
        data=load_json('test.json')
        data[args.doc_type].pop(args.ruleid)
        json.dump(data, open("test.json","w"))
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
    print("Rules Updated Succesfully")    
    # print(data)
    # print(jinn)    

if __name__ == "__main__":
    main()
