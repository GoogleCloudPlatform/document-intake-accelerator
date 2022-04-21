import pytest
from setup_e2e import create_test_table, delete_dataset

@pytest.fixture(scope="session")
def setup():
  create_test_table()
  yield
  delete_dataset()
