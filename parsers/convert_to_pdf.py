# importing necessary libraries

import img2pdf
from PIL import Image
import os
import random

dl_image_folder = "dl-docs/dl-images"
dl_pdf_folder = "dl-docs/dl-pdfs"

inp_img_folders = os.listdir(dl_image_folder)

for each_folder in inp_img_folders:

    inp_imgs = os.listdir(os.path.join(dl_image_folder, each_folder))
    random.shuffle(inp_imgs)

    for each_img in inp_imgs:

        # storing image path
        img_path = os.path.join(dl_image_folder, each_folder, each_img)
        pdf_path = "{}.pdf".format(os.path.join(dl_pdf_folder, each_folder, each_img.split('.')[0]))

        # opening image
        image = Image.open(img_path)

        # converting into chunks using img2pdf
        pdf_bytes = img2pdf.convert(image.filename)

        # opening or creating pdf file
        file = open(pdf_path, "wb")

        # writing pdf files with chunks
        file.write(pdf_bytes)

        # closing image file
        image.close()

        # closing pdf file
        file.close()

# output
print("Process Completed")