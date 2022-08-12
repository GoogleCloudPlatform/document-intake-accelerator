#Creating a bigquery dataset and table schema

resource "google_bigquery_dataset" "data_set" {
  dataset_id    = "validation"
  friendly_name = "Validation Dataset"
  description   = "BQ dataset for validation process"
  location      = "US"
}

resource "google_bigquery_table" "table_id" {
  dataset_id          = "validation"
  table_id            = "validation_table"
  deletion_protection = "false"

  schema = <<EOF
[
  {
    "name": "case_id",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "uuid",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "document_class",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "document_type",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "entities",
    "type": "STRING",
    "mode": "NULLABLE"
  }


]
EOF

}