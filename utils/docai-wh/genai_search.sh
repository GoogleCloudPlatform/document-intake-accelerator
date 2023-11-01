#!/bin/bash

if [[ -z "${DOCAI_WH_PROJECT_ID}" ]]; then
  echo DOCAI_WH_PROJECT_ID env variable is not set.
  exit
fi

TOKEN=$(gcloud auth application-default print-access-token)
USER=`whoami`
PROJECT_NUM=$(gcloud projects describe "$DOCAI_WH_PROJECT_ID" --format='get(projectNumber)')
ENDPOINT="https://contentwarehouse.googleapis.com/v1/projects/$PROJECT_NUM/locations/us/documents:search"

echo "Please input your question below:"
#QUESTION="Tell me about Linda Ortiz?"
read user_question

# To identify the documents which are close/relevant to the natural-language search query
# (no of documents can be controlled with the field - qa_size_limit)
REQUEST='{
  "document_query":
  {
    "query": "'"$user_question"'",
    "is_nl_query": "true"
  },
  "qa_size_limit": "10",
  "request_metadata": {
    "user_info": {
      "id": "user:'"$USER"'@google.com",
      "group_ids": []
    }
  }
}'

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$REQUEST" \
  $ENDPOINT > temp.json

cat temp.json | jq -r '.matchingDocuments[] | "\"\(.document.name)\","'  > documents.txt

#  Once we have the document id's  we need to run the query again limiting to those document/documents
#  based on confidence_score
DOCUMENTS=$(cat documents.txt)
REQUEST='{
   "document_query": {
    "query": "'"$user_question"'",
       "is_nl_query": "true",
       "document_name_filter": ['"$DOCUMENTS"']
   },
   "qa_size_limit": "1",
   "request_metadata": {
       "user_info": {
           "id": "user:'"$USER"'@google.com",
       }
   }
}'

curl -X POST \
  -H "Authorization: Bearer $TOKEN"  \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "$REQUEST" \
  $ENDPOINT > response.json

echo "Here is the answer:"
cat response.json | jq -r '.questionAnswer'

rm documents.txt
rm temp.json
rm response.json
