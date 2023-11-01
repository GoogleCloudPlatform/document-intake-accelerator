#!/bin/bash
# Re-index old/existing documents post enabling GenAI Search in Document AI Warehouse


TOKEN=$(gcloud auth application-default print-access-token)
USER=`whoami`
PROJECT_NUM=$(gcloud projects describe "$DOCAI_WH_PROJECT_ID" --format='get(projectNumber)')

ENDPOINT="https://contentwarehouse.googleapis.com/v1/projects/$PROJECT_NUM/locations/us/documents:search"
REQUEST='{
  "require_total_size": true,
  "page_size": 100,
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

# Append first 100 documents to documents.txt and output the total number of documents to update
cat temp.json | jq -r '.matchingDocuments[] | "\(.document.name),\(.document.documentSchemaName)"' > documents.txt

TOTAL_DOCUMENTS=`cat temp.json | jq -r '.totalSize'`
echo "Updating $TOTAL_DOCUMENTS documents"

# Call the /search API until there are no more documents
NEXT_PAGE_TOKEN=`cat temp.json | jq -r '.nextPageToken'`
while [ "$NEXT_PAGE_TOKEN" != "null" ]
do
    REQUEST='{
    "page_token": "'"$(echo "$NEXT_PAGE_TOKEN" | sed 's/"/\\"/g')"'",
    "page_size": 100,
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

    # Append next 100 documents to documents.txt
    cat temp.json | jq -r '.matchingDocuments[] | "\(.document.name),\(.document.documentSchemaName)"' >> documents.txt 2>/dev/null

    # Get the next page token if there is a next page
    if grep -q "nextPageToken" temp.json; then
        NEXT_PAGE_TOKEN=`cat temp.json | jq -r '.nextPageToken'`
    else
        NEXT_PAGE_TOKEN="null"
    fi
done

# Loop through every line in documents.txt
while IFS=, read -r DOCUMENT DOCUMENT_SCHEMA_NAME
do
    # Patch (update) the document to trigger Gen AI indexing
    ENDPOINT="https://contentwarehouse.googleapis.com/v1/$DOCUMENT"
    REQUEST='{
    "document": {
        "documentSchemaName": "'$DOCUMENT_SCHEMA_NAME'",
    },
    "update_options": {
        "update_type": "UPDATE_TYPE_MERGE"
    },
    "request_metadata": {
        "user_info": {
        "id": "user:'"$USER"'@google.com",
        "group_ids": []
        }
    }
    }'

    curl -s -X PATCH \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$REQUEST" \
    $ENDPOINT > temp.json

    cat temp.json | jq -r '.document.name'
done < documents.txt

rm documents.txt
rm temp.json
