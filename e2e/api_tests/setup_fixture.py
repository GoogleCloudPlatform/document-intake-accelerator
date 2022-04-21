import pytest
from setup_e2e import create_table,delete_dataset

pytest.fixture(scope="session")
def create_db():
  create_table()

pytest.fixture(scope="session")
def cleanup():
  delete_dataset()