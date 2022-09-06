"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# script to convert png to pdf
import os
from os import listdir
from PIL import Image
import img2pdf
import re

# get the path/directory.Here as an example utility bills has been taken
folder_dir = "fake_data_generator/UtilityBills-arizona"
pdf_path = "fake_data_generator/utility-bill-arizona"
ct=1
image_list=[]
file_name='arizona-utility-bill-'
for images in os.listdir(folder_dir):
    image_list.append(images)

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

image_list.sort(key=natural_keys)
print(image_list)
print(len(image_list))

for images in image_list:
    # check if the image ends with png
    if (images.endswith(".png")):
        print(ct)
        image_1 = Image.open(folder_dir+"/"+images)
        im_1 = image_1.convert('RGB')
        im_1.save(pdf_path+"/"+file_name+str(ct)+'.pdf')
        ct=ct+1