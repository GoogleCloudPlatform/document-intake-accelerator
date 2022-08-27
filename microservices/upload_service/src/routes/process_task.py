""" Process task api endpoint """
from fastapi import APIRouter, BackgroundTasks, status
from models.process_task import ProcessTask
from utils.process_task_helpers import run_pipeline
# pylint: disable = ungrouped-imports
from common.utils.logging_handler import Logger
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR

router = APIRouter()
SUCCESS_RESPONSE = {"status": STATUS_SUCCESS}
FAILED_RESPONSE = {"status": STATUS_ERROR}


@router.post("/process_task", status_code=status.HTTP_202_ACCEPTED)
async def process_task(payload: ProcessTask,
                       background_task: BackgroundTasks,
                       is_hitl: bool = False,
                       is_reassign: bool = False):
  """Process task runs the ML pipeline

  Args:
    payload (ProcessTask): Consist of configs required to run the pipeline
    background_task : It is used to run the ML tasks in the background
    is_hitl : It is used to run the pipeline for unclassifed documents
    is_reassign : It is used to run the pipeline for reassigned document
  Returns:
    202 : Documents are being processed
    422 : Invalid json provided
    """
  payload = payload.dict()
  Logger.info(f"Processing the documents : {payload}")
  # Run the pipeline in the background
  background_task.add_task(run_pipeline, payload, is_hitl, is_reassign)
  return {"message": "Processing your document"}
