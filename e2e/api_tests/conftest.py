import pytest
from setup_e2e import create_test_table, delete_dataset
#create_bucket_class_location

@pytest.fixture(scope="session")
def setup():
  create_test_table()
  # create_bucket_class_location()
  yield
  delete_dataset()


