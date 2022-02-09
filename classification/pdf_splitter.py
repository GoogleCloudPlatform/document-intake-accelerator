from datetime import datetime
import os
import argparse
from PyPDF2 import PdfFileReader, PdfFileWriter, pdf
try:
    import fitz
except:
    print(__file__, "needs PyMuPDF (fitz).")
    raise SystemExit

if not tuple(map(int, fitz.version[0].split("."))) >= (1, 18, 18):
    raise SystemExit("require PyMuPDF v1.18.18+")


class PDFManager:

    def __init__(self, pdf_file, out_path):
        self.inp_file_pdf = pdf_file
        self.out_path = out_path        
        self.timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        self.inp_doc = fitz.open(self.inp_file_pdf)

    def split_and_save2pdf(self) -> list :
        """ 
        Splits all the pages of pdf file and save them to pdf
        Returns:
        """
        with open(self.inp_file_pdf, 'rb') as fd:
            reader_obj = PdfFileReader(fd)
            for i in range(reader_obj.numPages):
                self.save_to_pdf(i, reader_obj.getPage(i))
    
    def split_save2img(self, page_num=0, save=True):
        """ 
        Generates an image for the first page of the PDF doc
        Returns:
        """
        if page_num < self.inp_doc.page_count:
            return self.save2image(page_num, self.inp_doc.load_page(page_num), save)
        else:
            print("Page number doesnot exist")
            exit(-1)

    def split_all_save2img(self, save=True):
        """ 
        Splits all the pages into images.
        Returns:
        """

        for pg_num in range(self.inp_doc.page_count):
            self.split_save2img(self, pg_num, save=True)


    def save2image(self,pg_num, page, save):
        file_name = self.timestamp + '_' + os.path.basename(self.inp_file_pdf)
        pix = page.get_pixmap()
        output = os.path.join(
            self.out_path, file_name[:-4] + "_%s.png"% str(pg_num))    
        if save: 
            pix.save(output)
            return output
        else:
            return page
        
    
    def save_to_pdf(self, page_num, page):

        writer = PdfFileWriter()
        writer.addPage(page)

        file_name = self.timestamp + '_' + os.path.basename(self.inp_file_pdf) 
        file_name = os.path.join(self.out_path, file_name[:-4] + "%s.pdf"% str(page_num))

        with open(file_name, "wb") as out_stream:
            writer.write(out_stream)


def get_parser():
  # Read command line arguments
    parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      Script used to generate pdf/images for each pages in a pdf.
      """,
      epilog="""
      Examples:
      python pdf_splitter.py --inp_pdf_path=path-to-file.pdf --output=path-to-output-folder
      """)
    parser.add_argument(
        "--inp_pdf_path",
        default="data/Illinois_filled.pdf",
        help="Path to input pdf file")
    parser.add_argument(
        "--output",
        default="data/images",
        help="Path to the destination output pdf/image file")
    
    parser.add_argument(
        "--split_into",
        default="images",
        help="Type of conversion need on pages of a pdf file")

    return parser

if __name__ == "__main__":
    
    parser = get_parser()
    args = parser.parse_args()

    ## Comment/delete later these 4 lines below
    path = "/Users/sumitvaise/Downloads/Dataset/Arkansas/UE_forms"
    outpath = "/Users/sumitvaise/Downloads/Dataset/Arkansas/UE_Imgs"

   # args['inp_pdf_path'], args['output'] = path, outpath


    #########
    # pdf_manager = PDFManager(args['inp_pdf_path'], args['output'])
    

    files = os.listdir(path)

    for i_file in files:
        file_path = os.path.join(path, i_file)
        pdf_manager = PDFManager(file_path, outpath)

        # extract any random page in image format of a pdf file
        page_num=0 # front page
        pdf_manager.split_save2img(page_num=0, save=True)

    # if args['split_into'] is 'images':
    #     pdf_manager.split_all_save2img()
    # else:
    #     pdf_manager.split_and_save2pdf()
    
