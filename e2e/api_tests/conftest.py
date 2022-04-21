import pytest
from setup_e2e import create_table, delete_dataset

@pytest.fixture(scope="session")
def setup():
  create_table()
  yield
  delete_dataset()
