import asyncio

from google.cloud import storage
import sys
import os

from starlette.concurrency import run_in_threadpool

sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../cloudrun/startpipeline/src'))

from common.utils.helper import split_uri_2_path_filename
from utils.run_pipeline import run_pipeline
gcs = storage.Client()

# Get List of Document Objects from the Output Bucket
bucket_name = "cda-ext-iap-pa-forms"
file_uri = "1683151747/START_PIPELINE"

loop = asyncio.get_event_loop()
tasks = [
    loop.create_task(run_pipeline(bucket_name, file_uri))
]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()

