"""
  Dummy extraction function
"""


def extract_entities(gcs_url, doc_class, context):
  """

    Creating a dummy output for extraction ML function

  """
  print({gcs_url}, {doc_class}, {context})
  final_extracted_entities = [{
      'entity': 'employer_address',
      'value': '012 James Mission Melanieton, MS 25712',
      'corrected_value': None,
      'extraction_confidence': 0.76,
      'manual_extraction': False
  }, {
      'entity': 'name',
      'value': 'CHRISTOPHER J LEWIS',
      'extraction_confidence': 0.93,
      'corrected_value': None,
      'manual_extraction': False
  }, {
      'entity': 'pay_period_to',
      'value': '2021-10-31',
      'extraction_confidence': 0.7,
      'corrected_value': None,
      'manual_extraction': False
  }, {
      'entity': 'ytd',
      'value': '20507.71',
      'extraction_confidence': 0.92,
      'corrected_value': None,
      'manual_extraction': False
  }, {
      'entity': 'pay_date',
      'value': '2021-11-01',
      'extraction_confidence': 0.93,
      'corrected_value': None,
      'manual_extraction': False
  }, {
      'entity': 'ssn',
      'value': '328-07-7635',
      'extraction_confidence': 0.82,
      'corrected_value': None,
      'manual_extraction': False
  }, {
      'entity': 'pay_period_from',
      'value': '2021-10-01',
      'extraction_confidence': 0.48,
      'corrected_value': None,
      'manual_extraction': False
  }, {
      'entity': 'employer_name',
      'value': 'Derek Smith',
      'corrected_value': None,
      'extraction_confidence': None,
      'manual_extraction': True
  }, {
      'entity': 'rate',
      'value': '34',
      'extraction_confidence': None,
      'corrected_value': None,
      'manual_extraction': True
  }, {
      'entity': 'hours',
      'value': '180',
      'corrected_value': None,
      'extraction_confidence': None,
      'manual_extraction': True
  }]
  document_extraction_confidence = 0.9
  return final_extracted_entities, document_extraction_confidence

