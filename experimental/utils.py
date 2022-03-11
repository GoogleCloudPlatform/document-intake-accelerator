from google.cloud import storage
import os
import math
import re
from collections import Counter

WORD = re.compile(r"\w+")

def download_file_gcs(bucket_name=None, gcs_uri=None, file_to_download=None, output_filename=None):
    """Function takes a path of an object/file stored in GCS bucket and downloads
    the file in the current working directory

    Args:
        bucket_name (str): bucket name from where file to be downloaded
        gcs_uri (str): GCS object/file path
        output_filename (str): desired filename
        file_to_download (str): gcs file path excluding bucket name.
            Ex: if file is stored in X bucket under the folder Y with filename ABC.txt
            then file_to_download = Y/ABC.txt
    Return:
    """
    if bucket_name is None:
        bucket_name = gcs_uri.split('/')[2]
    
    # if file to download is not provided it can be extracted from the GCS URI
    if file_to_download is None and gcs_uri is not None:
        file_to_download = '/'.join(gcs_uri.split('/')[3:])

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(file_to_download)

    if output_filename is None:
        output_filename = file_to_download
    with open(output_filename, "wb") as file_obj:
        blob.download_to_file(file_obj)
        
    return output_filename


def get_cosine(str1, str2):
    vec1 = text_to_vector(str1)
    vec2 = text_to_vector(str2)
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)

if __name__ == '__main__':
    client_id=1
    u_id = 2
    output_filename = str(client_id)+ '_' + str(u_id) +'_claim.pdf'

    #Example1:  Extraction of pdf file using GCS URI
    # download_pdf_gcs(
    #     gcs_uri='gs://claim-processing-classification-dataset/Arizona_claim22.pdf',
    #     output_filename=output_filename
    # )

    #Example 2:  Extraction of pdf file using bucket name and file path in the same bucket
    # download_file_gcs(
    #     bucket_name='claim-processing-classification-dataset',
    #     file_to_download='Arizona_claim22.pdf',
    #     output_filename=output_filename
    # )

    # Example 3 for cosine matching
    text1 = "This is a foo bar sentence ."
    text2 = "This sentence is similar to a foo bar sentence ."

    cosine = get_cosine(text1, text2)

    print("Cosine:", cosine)