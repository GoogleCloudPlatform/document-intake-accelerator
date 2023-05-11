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

from PIL import Image
# In this example we are merging pngs to a single pdf for Arizona State
for i in range(1,6):

        image1 = Image.open(r'fake_data_generation/arizona-test-form-'+str(i)+'.png')
        image2 = Image.open(r'fake_data_generation/arizona-test-form2-'+str(i)+'.png')
        image3 = Image.open(r'fake_data_generation/arizona-test-form3-'+str(i)+'.png')

        im1 = image1.convert('RGB')
        im2 = image2.convert('RGB')
        im3 = image3.convert('RGB')

        imagelist = [im2,im3]
        print(i)
        im1.save(r'fake_data_generation/Arizona'+str(i)+'.pdf', save_all=True, append_images=imagelist)