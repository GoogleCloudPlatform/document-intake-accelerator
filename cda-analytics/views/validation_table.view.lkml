view: validation_table {
  sql_table_name: `validation.validation_table`
    ;;

  dimension: case_id {
    type: string
    description: "CASE id of the application"
    sql: ${TABLE}.case_id ;;
  }

  dimension: document_class {
    type: string
    description: "Indicates document_class and processor used for extracting the form."
    sql: ${TABLE}.document_class ;;
  }

  dimension: document_type {
    type: string
    description: "Document type if known"
    sql: ${TABLE}.document_type ;;
  }

  dimension: entities {
    type: string
    description: "Raw entities extracted from the document."
    sql: ${TABLE}.entities ;;
  }

  dimension: gcs_doc_path {
    type: string
    description: "GCS path to the document"
    sql: ${TABLE}.gcs_doc_path ;;
  }

  dimension_group: timestamp {
    type: time
    description: "Timestamp when row was added"
    timeframes: [
      raw,
      time,
      date,
      week,
      month,
      quarter,
      year
    ]
    datatype: datetime
    sql: ${TABLE}.timestamp ;;
  }

  dimension: uid {
    type: string
    description: "Unique key"
    sql: ${TABLE}.uid ;;
  }

  measure: count {
    type: count
    drill_fields: []
  }
}
