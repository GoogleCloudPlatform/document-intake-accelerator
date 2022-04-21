import pytest
from setup_e2e import create_table, delete_dataset

@pytest.fixture(scope="function")
def setup():
  print("=============CREATING TABLE=============")
  create_table()
  yield
  print("=============DELETING TABLE=============")
  delete_dataset()