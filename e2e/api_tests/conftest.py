import pytest
from setup_e2e import create_table, delete_dataset

@pytest.fixture(scope="function")
def setup():
  print("=============CREATING TABLE=============")
  create_table()
  yield
  delete_dataset()
  print("=============DELETING TABLE=============")
