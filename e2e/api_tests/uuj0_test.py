import requests
from endpoint_proxy import get_baseurl


def test_api_ping():
  base_url = get_baseurl("sample-service")
  res = requests.get(base_url + "/ping")
  assert res.status_code == 200


def test_non_exist_endpoint():
  base_url = get_baseurl("sample-service")
  res = requests.get(base_url + "/sample-service/not-exist")
  print(base_url)
  assert res.status_code == 404
