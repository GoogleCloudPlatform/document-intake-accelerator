echo "Cleaning upload directory inside ProjectID=[${PROJECT_ID}] gs://${PROJECT_ID}-document-upload"
gsutil -m rm -a -r gs://"${PROJECT_ID}-document-upload/**"