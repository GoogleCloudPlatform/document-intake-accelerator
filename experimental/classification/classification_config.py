"""
Configuration parameter for classification.
"""
# Prediction Confidence threshold for the classifier to reject any prediction less than the threshold value.
conf_thresh=0.98

# Project Id for billing purpose and this Id also signifies the access to the prediction API
# If the project doesnot have access to the prediction API code will fail!
project_id='claims-processing-dev'

# Endpoint Id where model is deployed.
endpoint_id='4679565468279767040'