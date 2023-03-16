import argparse
import os

import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../cloudrun/startpipeline/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../common/src'))

from utils import trigger_upload
trigger_upload.upload_file(
    bucket_name="ek-cda-engine",
    files=["sample_data/bsc_demo/bsc-dme-pa-form-1.pdf"],
    case_id="123456")
