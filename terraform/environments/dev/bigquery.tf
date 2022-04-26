#Creating a bigquery dataset and table schema

resource "google_bigquery_dataset" "data_set" {
  dataset_id                  = var.dataset_name
  friendly_name               = "test"
  description                 = "This is a bigquery dataset"
  location                    = "US"

}

resource "google_bigquery_table" "table_id" {
  dataset_id = google_bigquery_dataset.data_set.dataset_id
  table_id   = var.table_name
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