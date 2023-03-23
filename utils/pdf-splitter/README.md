# Document AI PDF Splitter Utility

This project uses Document AI Splitter/Classifier Processors identify split points and uses PikePDF to split PDF documents.

For more information about Document AI Splitters, check out [Document splitters behavior](https://cloud.google.com/document-ai/docs/splitters)

## Quick start

1. Install the prerequisites: 
```shell
    cd utils/pdf-splitter
    pip install -r requirements.txt
```
2. Granting Access and Permissions
   1. When running from the development machine, setup application default authentication, run: `gcloud auth application-default login`
   2. When running from Cloud Shell, need to set `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to the service account key with following storage and docai roles:
      Service account with [DOCA permissions](https://cloud.google.com/document-ai/docs/access-control/iam-roles) and read/write access to the bucket:

    ```shell
    export DOCAI_PROJECT_ID=<doca-project-id>
    gcloud config set project $DOCAI_PROJECT_ID
    ```

    ```shell
    SA_NAME=cda-docai
    gcloud iam service-accounts create $SA_NAME \
            --description="docai invoker" \
            --display-name="cda docai invoker"
        
    # DOCAI Access
    gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
            --member="serviceAccount:${SA_NAME}@${DOCAI_PROJECT_ID}.iam.gserviceaccount.com" \
            --role="roles/documentai.apiUser"
    gcloud projects add-iam-policy-binding $DOCAI_PROJECT_ID \
            --member="serviceAccount:${SA_NAME}@${DOCAI_PROJECT_ID}.iam.gserviceaccount.com" \
            --role="roles/documentai.editor"
              
    gcloud iam service-accounts keys create cda_docai_key \
            --iam-account=cda-docai@$DOCAI_PROJECT_ID.iam.gserviceaccount.com
                    
    export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/cda_docai_key
    echo $GOOGLE_APPLICATION_CREDENTIALS
    ```
   
    When using Cloud Storage Buckets for input and output, additional steps are required:

     ```shell
    export IN_BUCKET=gs://<path-to-input>
    export OUT_BUCKET=gs://<path-to-output>
     ```
   
    ```shell
      # Cloud Storage Access
      gcloud storage buckets add-iam-policy-binding  ${IN_BUCKET}  \
          --member="serviceAccount:$SA_NAME@$DOCAI_PROJECT_ID.iam.gserviceaccount.com" \
          --role="roles/storage.objectViewer"
      gcloud storage buckets add-iam-policy-binding  ${OUT_BUCKET}  \
          --member="serviceAccount:$SA_NAME@$DOCAI_PROJECT_ID.iam.gserviceaccount.com" \
          --role="roles/storage.admin"
   
      # Grant DocAI service account access to the buckets:
      PROJECT_DOCAI_NUMBER=$(gcloud projects describe "$DOCAI_PROJECT_ID" --format='get(projectNumber)')
      gcloud storage buckets add-iam-policy-binding  ${OUT_BUCKET} --member="serviceAccount:service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com" --role="roles/storage.admin"
      gcloud storage buckets add-iam-policy-binding  ${IN_BUCKET} --member="serviceAccount:service-${PROJECT_DOCAI_NUMBER}@gcp-sa-prod-dai-core.iam.gserviceaccount.com" --role="roles/storage.objectViewer"

    ```



3. Run the sample on a single local file (-f): 
```shell
python main.py -f <local-path-to-combined-document>.pdf --project-id <DOCAI_PROJECT_ID>  --processor-id <SPLITTER_ID> -o <local-path-to-the-output-directory>
```
    - You should see the split up sub-documents in your current directory with file
    names like `pg1-2_1040sc_2020_document`.
    - You should also see the raw [`Document`](https://cloud.google.com/document-ai/docs/reference/rest/v1/Document) output from Document AI in a json file `multi_document.json`

4. Run the sample on a GCS directory  (-d):

```shell
python main.py -d gs://<bucket/path/to/folder> --project-id <DOCAI_PROJECT_ID>  --processor-id <SPLITTER_ID> -o gs://<output_bucket/path/to/folder>
```




