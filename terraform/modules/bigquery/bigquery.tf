/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

#Creating a bigquery dataset and table schema

resource "google_bigquery_dataset" "data_set" {
  dataset_id    = var.dataset_id
  friendly_name = "Validation Dataset"
  description   = "BQ dataset for validation process"
  location      = "US"
  labels = {
    goog-packaged-solution = "prior-authorization"
  }
}

resource "google_bigquery_table" "table_id" {
  depends_on = [
    google_bigquery_dataset.data_set
  ]

  deletion_protection = false
  dataset_id          = "validation"
  table_id            = "validation_table"

  schema = <<EOF
[
    {
        "name": "uid",
        "type": "STRING",
        "mode": "REQUIRED",
        "description": "Unique key"
    },
    {
        "name": "case_id",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "CASE id of the application"
    },
    {
        "name": "document_class",
        "type": "STRING",
        "mode": "REQUIRED",
        "description": "Indicates document_class and processor used for extracting the form."
    },
    {
        "name": "ocr_text",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "OCR Plain text of the extracted form."
    },
    {
        "name": "classification_score",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Score for the classification prediction."
    },
    {
        "name": "is_hitl_classified",
        "type": "BOOL",
        "mode": "NULLABLE",
        "description": "Indicates if classification was done manually."
    },
    {
        "name": "document_type",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Document type if known"
    },
    {
        "name": "entities",
        "type": "JSON",
        "mode": "NULLABLE",
        "description": "Raw entities extracted from the document."
    },
    {
        "name": "timestamp",
        "type": "DATETIME",
        "mode": "REQUIRED",
        "description": "Timestamp when row was added"
    },
    {
        "name": "gcs_doc_path",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "GCS path to the document"
    }


]
EOF

}
