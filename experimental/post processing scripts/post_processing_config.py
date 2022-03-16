''' 
This is a config file for post-processing script. 
If the user wants to post process any extracted field value he can make changes to this file.
The post processing script handles the following:
1. Cleans any noise in the extracted value.
2. Converts a value to its upper case
3. Converts a value to its lower case.
3. Change date format.
4. Removes extra spaces in extracted value.
5. Corrects extracted value to string.
6. Corrects extracted value to number.

For date formats user can use below symbols:
%d Day of the month as a zero-padded decimal number eg.01, 02, …, 31
%b Month as locale’s abbreviated name eg.Jan, Feb, …, Dec (en_US);
%B Month as locale’s full name eg.January, February, …, December (en_US);
%m Month as a zero-padded decimal number eg:01, 02, …, 12
%y Year without century as a zero-padded decimal number eg:00, 01, …, 99
%Y Year with century as a decimal number eg:0001, 0002, …, 2013, 2014, …, 9998, 9999
eg: 03/04/2022 is '%m/%d/%y'
'''
#Template to be used to convert to string(based on observation).
#The dictionary keys are the OCR extracted characters and 
#dictionary values are the actual values to be populated.
num_to_str_dict={'8':'B','0':'0','1':'I','4':'A','5':'S'}

#Template to be used to convert to number(based on observation).
#The dictionary keys are the OCR extracted characters and 
#dictionary values are the actual values to be populated.
str_to_num_dict={'B':'8','O':'0','I':'1','A':'4','S':'5'}

#dictionary to clean extracted values.
#eg: if input_dict={'dob':'2021-12-04\n'} then we have noise='\n'
#So we pass clean_value_dict={'dob':'\n'}
#In case dob key has different noise for different document create clean_value_dict={'dob':['noise1','noise2']}
clean_value_dict={'dob':['\n']} 

#list for extracted values to be in upper case.
#The list items are the key names.
lower_to_upper_list=['name']

#list for extracted values to be in lower case.
#The list items are the key names.
upper_to_lower_list=['address']

#list to remove extra spaces in extracted values.
#The list items are the key names.
clean_space_list=['name']

#dictionary to update date format.
#The dictionary key values are the key field names and the dictionary values
#are list of two input items. first item is input_date_format and second item is output date format.
date_format_dict={'dob':['%Y-%m-%d','%y/%m/%d']}

#list of key fields for which extracted values are needed to be corrected to string
#will be based on num_to_str_dict
convert_to_string=['name']

#list of key fields for which extracted values are needed to be corrected to integer
#will be based on str_to_num_dict. 
convert_to_number=['phone_no']










                     