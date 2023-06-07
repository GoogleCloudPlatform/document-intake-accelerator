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

  dimension: form {
    type: string
    sql: ${TABLE}.gcs_doc_path ;;
    html:
    <a style="color: blue; border-bottom: 1px solid blue" href="https://storage.cloud.google.com/{% assign len = value.size %}{{ value | slice: 5, len }}" target="_blank" rel="noopener noreferrer">
        {{ all_forms.document_class }}
    </a> ;;
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
    map_layer_name: us_states
    sql: ${TABLE}.value ;;
  }

  measure: count {
    type: count
  }

  measure:  count_of_medical_forms{
    type: count_distinct
    label: "Medical Forms"
    sql: ${TABLE}.uid ;;
    link: {
      label: "Medical Forms"
      url: "https://1983221b-52a8-4c01-be65-29f2cde0d012.looker.app/dashboards/8"
      icon_url: "http://google.com/favicon.ico"
    }
    filters: [document_class: "'generic_form','health_intake_form'"]
  }

  measure:  count_of_fax_cover_page{
    type: count_distinct
    label: "FAX Cover Page"
    sql: ${TABLE}.uid ;;
    link: {
      label: "FAX Cover Page"
      url: "https://1983221b-52a8-4c01-be65-29f2cde0d012.looker.app/dashboards/9"
      icon_url: "http://google.com/favicon.ico"
    }
    filters: [document_class: "fax_cover_page"]
  }
}
