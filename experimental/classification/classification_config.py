"""
Configuration parameter for classification.
"""
#Prediction Confidence threshold for the classifier to reject any prediction
#less than the threshold value.
CONF_THRESH = 0.98

#Project Id for billing purpose and this Id also signifies the access to
#the prediction API
#If the project doesnot have access to the prediction API code will fail!
PROJECT_ID = 'claims-processing-dev'

#Endpoint Id where model is deployed.
ENDPOINT_ID = '4679565468279767040'
