# Document AI PDF Splitter Utility

This project uses Document AI Splitter/Classifier Processors identify split points and uses PikePDF to split PDF documents.

For more information about Document AI Splitters, check out [Document splitters behavior](https://cloud.google.com/document-ai/docs/splitters)

## Quick start

1. Install the prerequisites: 
```shell
    cd utils/pdf-splitter
    pip install -r requirements.txt
```
2. Setup application default authentication, run: `gcloud auth application-default login`
3. Run the sample: `python main.py -f <local-path-to-combined-document>.pdf --project-id <DOCAI_PROJECT_ID>  --processor-id <SPLITTER_ID> -o <local-path-to-the-output-directory>`
    - You should see the split up sub-documents in your current directory with file
    names like `pg1-2_1040sc_2020_document`.
    - You should also see the raw [`Document`](https://cloud.google.com/document-ai/docs/reference/rest/v1/Document) output from Document AI in a json file `multi_document.json`

4. Run the sample on Cloud Storage directory: 
```shell
python main.py -d <gs://bucket/path/to/folder> --project-id <DOCAI_PROJECT_ID>  --processor-id <SPLITTER_ID> -o <gs://output_bucket/path/to/folder>
```


