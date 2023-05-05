curl -X GET \
-H "Authorization: Bearer "$(gcloud auth application-default print-access-token) \
-H "Content-Type: application/json; charset=utf-8" \
-d @request.json \
https://us-documentai.googleapis.com/v1/projects/$PROJECT_ID/locations/us:fetchProcessorTypes