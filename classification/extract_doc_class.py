import cv2
import os
import argparse
import easyocr
from .pdf_splitter import PDFManager as pdf

class LabelExtractor:
    def __init__(self) -> None:
        pass
    def classify(self, doc_path) -> str:
        """ 1.load the number of classes from the config.
            2. Obtain image of the front page.
            3. send it to OCR for text fields extraction
            4. Compare with the pre-defined classes.
        Args:pip  
            doc_path[str]: path to the pdf file.
        """
        pdf_manager = pdf(doc_path)

        # extract first image.
        page = pdf_manager.inp_doc[0]
        first_page_img = pdf_manager.save2image(0, page, save=False)

        # send it to OCR
        bbox, text = self.extract_fields(first_page_img)
        # compare the text under the bbox with the classes

        return

    def extract_fields(self, image_arr):
        """ Applies OCR to extract the text from the images
        """
        reader = easyocr.Reader(['en'])
        bounds = reader.readtext(image_arr)
        return


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

    path = "/Users/sumitvaise/DOCAI/claims-processing/classification/data/Illinois_filled.pdf"
    outpath = "/Users/sumitvaise/DOCAI/claims-processing/classification/data/images"



