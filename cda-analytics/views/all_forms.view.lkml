view: all_forms {
  sql_table_name: `validation.all_forms`
    ;;

  dimension: case_id {
    type: string
    sql: ${TABLE}.case_id ;;
  }

  dimension: confidence {
    type: number
    sql: ${TABLE}.confidence ;;
  }

  dimension: corrected_value {
    type: string
    sql: ${TABLE}.corrected_value ;;
  }

  dimension: document_class {
    type: string
    sql: ${TABLE}.document_class ;;
  }

  dimension: document_type {
    type: string
    sql: ${TABLE}.document_type ;;
  }

  dimension: gcs_doc_path {
    type: string
    sql: ${TABLE}.gcs_doc_path ;;
  }

  dimension: name {
    type: string
    sql: ${TABLE}.name ;;
  }

  dimension_group: timestamp {
    type: time
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
    sql: ${TABLE}.uid ;;
  }

  dimension: value {
    type: string
    sql: ${TABLE}.value ;;
  }

  measure: count {
    type: count
    drill_fields: [name]
  }
}
