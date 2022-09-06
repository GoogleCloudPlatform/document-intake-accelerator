"""
Module to perform operations on pdf files
"""
from datetime import datetime
import os
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter
import fitz

if tuple(map(int, fitz.version[0].split('.'))) < (1, 18, 18):
  raise SystemExit('require PyMuPDF v1.18.18+')


class PDFManager:
  """
  A class to perform operations on a pdf file.
  """

  def __init__(self, pdf_file, out_path):
    self.inp_file_pdf = pdf_file
    self.out_path = out_path
    self.timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
    self.input_doc = fitz.open(self.inp_file_pdf)

  def split_and_save2pdf(self) -> list:
    """
    Splits all the pages of pdf file and save them to pdf
    Returns:
    """
    with open(self.inp_file_pdf, 'rb') as fd:
      reader_obj = PdfFileReader(fd)
      for i in range(reader_obj.numPages):
        self.save_to_pdf(i, reader_obj.getPage(i))

  def split_save2img(self, page_num=0):
    """
    Generates an image for the first page of the PDF doc
    Returns:
    """
    if page_num < self.input_doc.page_count:
      return self.save2image(page_num, self.input_doc.load_page(page_num), True)
    else:
      print('Page number doesnot exist')
      sys.exit()

  def split_all_save2img(self):
    """
    Splits all the pages into images.
    Returns:
    """
    for page_num in range(self.input_doc.page_count):
      self.split_save2img(page_num)

  def save2image(self, page_num, page, save):
    """
    save a page in image format

    Args:
    page_num (int): page number
    page (pdf): page in pdf object type to be saved
    save (bool): whether to save or not.

    Returns:
    str: page/image
    """
    file_name = f'{self.timestamp}_{os.path.basename(self.inp_file_pdf)}'
    print(f"save2image originla PDF: {file_name}")

    pix = page.get_pixmap()
    output_filename = os.path.join(self.out_path,
                                   f'{file_name[:-4]}_{str(page_num)}.png')
    if save:
      pix.save(output_filename)
      return output_filename
    else:
      return page

  def save_to_pdf(self, page_num, page):
    """
    Save a page in pdf format

    Args:
    page_num (int): page number to be extracted and saved
    page (pdf): page object to be saved
    """
    writer = PdfFileWriter()
    writer.addPage(page)
    file_name = os.path.basename(self.inp_file_pdf)[:-4]
    file_name = file_name + '_' + self.timestamp + '.pdf'
    file_name = os.path.join(self.out_path,
                             f'{file_name[:-4]}_{str(page_num)}.pdf')
    with open(file_name, 'wb') as out_stream:
      writer.write(out_stream)
