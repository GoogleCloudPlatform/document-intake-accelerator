view: prior_auth_forms {
  sql_table_name: `validation.PRIOR_AUTH_FORMS`
    ;;

  dimension: __clinical_reason_for_urgency {
    type: string
    sql: ${TABLE}.__clinicalReasonForUrgency ;;
  }

  dimension: __gender_female {
    type: string
    sql: ${TABLE}.__genderFemale ;;
  }

  dimension: __gender_male {
    type: string
    sql: ${TABLE}.__genderMale ;;
  }

  dimension: __gender_other {
    type: string
    sql: ${TABLE}.__genderOther ;;
  }

  dimension: __gender_unknown {
    type: string
    sql: ${TABLE}.__genderUnknown ;;
  }

  dimension: __group_number {
    type: string
    sql: ${TABLE}.__groupNumber ;;
  }

  dimension: __issuer_date {
    type: string
    sql: ${TABLE}.__issuerDate ;;
  }

  dimension: __issuer_fax {
    type: string
    sql: ${TABLE}.__issuerFax ;;
  }

  dimension: __issuer_phone {
    type: string
    sql: ${TABLE}.__issuerPhone ;;
  }

  dimension: __member_id {
    type: string
    sql: ${TABLE}.__memberID ;;
  }

  dimension: __patient_do_b {
    type: string
    sql: ${TABLE}.__patientDoB ;;
  }

  dimension: __patient_name {
    type: string
    sql: ${TABLE}.__patientName ;;
  }

  dimension: __patient_phone {
    type: string
    sql: ${TABLE}.__patientPhone ;;
  }

  dimension: __pcp_fax {
    type: string
    sql: ${TABLE}.__pcpFax ;;
  }

  dimension: __pcp_name {
    type: string
    sql: ${TABLE}.__pcpName ;;
  }

  dimension: __pcp_phone {
    type: string
    sql: ${TABLE}.__pcpPhone ;;
  }

  dimension: __prev_auth_number {
    type: string
    sql: ${TABLE}.__prevAuthNumber ;;
  }

  dimension: __request_type_extension {
    type: string
    sql: ${TABLE}.__requestTypeExtension ;;
  }

  dimension: __request_type_initial {
    type: string
    sql: ${TABLE}.__requestTypeInitial ;;
  }

  dimension: __review_type_non_urgent {
    type: string
    sql: ${TABLE}.__reviewTypeNonUrgent ;;
  }

  dimension: __review_type_urgent {
    type: string
    sql: ${TABLE}.__reviewTypeUrgent ;;
  }

  dimension: __rp_contact_name {
    type: string
    sql: ${TABLE}.__rpContactName ;;
  }

  dimension: __rp_contact_phone {
    type: string
    sql: ${TABLE}.__rpContactPhone ;;
  }

  dimension: __rp_date {
    type: string
    sql: ${TABLE}.__rpDate ;;
  }

  dimension: __rp_fax {
    type: string
    sql: ${TABLE}.__rpFax ;;
  }

  dimension: __rp_name {
    type: string
    sql: ${TABLE}.__rpName ;;
  }

  dimension: __rp_npi {
    type: string
    sql: ${TABLE}.__rpNPI ;;
  }

  dimension: __rp_phone {
    type: string
    sql: ${TABLE}.__rpPhone ;;
  }

  dimension: __rp_specialty {
    type: string
    sql: ${TABLE}.__rpSpecialty ;;
  }

  dimension: __sp_fax {
    type: string
    sql: ${TABLE}.__spFax ;;
  }

  dimension: __sp_npi {
    type: string
    sql: ${TABLE}.__spNPI ;;
  }

  dimension: __sp_phone {
    type: string
    sql: ${TABLE}.__spPhone ;;
  }

  dimension: __sp_specialty {
    type: string
    sql: ${TABLE}.__spSpecialty ;;
  }

  dimension: __subscriber_name {
    type: string
    sql: ${TABLE}.__subscriberName ;;
  }

  dimension: case_id {
    type: string
    sql: ${TABLE}.case_id ;;
  }

  dimension: conf_clinical_reason_for_urgency {
    type: number
    sql: ${TABLE}.conf_clinicalReasonForUrgency ;;
  }

  dimension: conf_gender_female {
    type: number
    sql: ${TABLE}.conf_genderFemale ;;
  }

  dimension: conf_gender_male {
    type: number
    sql: ${TABLE}.conf_genderMale ;;
  }

  dimension: conf_gender_other {
    type: number
    sql: ${TABLE}.conf_genderOther ;;
  }

  dimension: conf_gender_unknown {
    type: number
    sql: ${TABLE}.conf_genderUnknown ;;
  }

  dimension: conf_group_number {
    type: number
    sql: ${TABLE}.conf_groupNumber ;;
  }

  dimension: conf_issuer_date {
    type: number
    sql: ${TABLE}.conf_issuerDate ;;
  }

  dimension: conf_issuer_fax {
    type: number
    sql: ${TABLE}.conf_issuerFax ;;
  }

  dimension: conf_issuer_phone {
    type: number
    sql: ${TABLE}.conf_issuerPhone ;;
  }

  dimension: conf_member_id {
    type: number
    sql: ${TABLE}.conf_memberID ;;
  }

  dimension: conf_patient_do_b {
    type: number
    sql: ${TABLE}.conf_patientDoB ;;
  }

  dimension: conf_patient_name {
    type: number
    sql: ${TABLE}.conf_patientName ;;
  }

  dimension: conf_patient_phone {
    type: number
    sql: ${TABLE}.conf_patientPhone ;;
  }

  dimension: conf_pcp_fax {
    type: number
    sql: ${TABLE}.conf_pcpFax ;;
  }

  dimension: conf_pcp_name {
    type: number
    sql: ${TABLE}.conf_pcpName ;;
  }

  dimension: conf_pcp_phone {
    type: number
    sql: ${TABLE}.conf_pcpPhone ;;
  }

  dimension: conf_prev_auth_number {
    type: number
    sql: ${TABLE}.conf_prevAuthNumber ;;
  }

  dimension: conf_request_type_extension {
    type: number
    sql: ${TABLE}.conf_requestTypeExtension ;;
  }

  dimension: conf_request_type_initial {
    type: number
    sql: ${TABLE}.conf_requestTypeInitial ;;
  }

  dimension: conf_review_type_non_urgent {
    type: number
    sql: ${TABLE}.conf_reviewTypeNonUrgent ;;
  }

  dimension: conf_review_type_urgent {
    type: number
    sql: ${TABLE}.conf_reviewTypeUrgent ;;
  }

  dimension: conf_rp_contact_name {
    type: number
    sql: ${TABLE}.conf_rpContactName ;;
  }

  dimension: conf_rp_contact_phone {
    type: number
    sql: ${TABLE}.conf_rpContactPhone ;;
  }

  dimension: conf_rp_date {
    type: number
    sql: ${TABLE}.conf_rpDate ;;
  }

  dimension: conf_rp_fax {
    type: number
    sql: ${TABLE}.conf_rpFax ;;
  }

  dimension: conf_rp_name {
    type: number
    sql: ${TABLE}.conf_rpName ;;
  }

  dimension: conf_rp_npi {
    type: number
    sql: ${TABLE}.conf_rpNPI ;;
  }

  dimension: conf_rp_phone {
    type: number
    sql: ${TABLE}.conf_rpPhone ;;
  }

  dimension: conf_rp_specialty {
    type: number
    sql: ${TABLE}.conf_rpSpecialty ;;
  }

  dimension: conf_sp_fax {
    type: number
    sql: ${TABLE}.conf_spFax ;;
  }

  dimension: conf_sp_npi {
    type: number
    sql: ${TABLE}.conf_spNPI ;;
  }

  dimension: conf_sp_phone {
    type: number
    sql: ${TABLE}.conf_spPhone ;;
  }

  dimension: conf_sp_specialty {
    type: number
    sql: ${TABLE}.conf_spSpecialty ;;
  }

  dimension: conf_subscriber_name {
    type: number
    sql: ${TABLE}.conf_subscriberName ;;
  }

  dimension: corrected_clinical_reason_for_urgency {
    type: string
    sql: ${TABLE}.corrected_clinicalReasonForUrgency ;;
  }

  dimension: corrected_gender_female {
    type: string
    sql: ${TABLE}.corrected_genderFemale ;;
  }

  dimension: corrected_gender_male {
    type: string
    sql: ${TABLE}.corrected_genderMale ;;
  }

  dimension: corrected_gender_other {
    type: string
    sql: ${TABLE}.corrected_genderOther ;;
  }

  dimension: corrected_gender_unknown {
    type: string
    sql: ${TABLE}.corrected_genderUnknown ;;
  }

  dimension: corrected_group_number {
    type: string
    sql: ${TABLE}.corrected_groupNumber ;;
  }

  dimension: corrected_issuer_date {
    type: string
    sql: ${TABLE}.corrected_issuerDate ;;
  }

  dimension: corrected_issuer_fax {
    type: string
    sql: ${TABLE}.corrected_issuerFax ;;
  }

  dimension: corrected_issuer_phone {
    type: string
    sql: ${TABLE}.corrected_issuerPhone ;;
  }

  dimension: corrected_member_id {
    type: string
    sql: ${TABLE}.corrected_memberID ;;
  }

  dimension: corrected_patient_do_b {
    type: string
    sql: ${TABLE}.corrected_patientDoB ;;
  }

  dimension: corrected_patient_name {
    type: string
    sql: ${TABLE}.corrected_patientName ;;
  }

  dimension: corrected_patient_phone {
    type: string
    sql: ${TABLE}.corrected_patientPhone ;;
  }

  dimension: corrected_pcp_fax {
    type: string
    sql: ${TABLE}.corrected_pcpFax ;;
  }

  dimension: corrected_pcp_name {
    type: string
    sql: ${TABLE}.corrected_pcpName ;;
  }

  dimension: corrected_pcp_phone {
    type: string
    sql: ${TABLE}.corrected_pcpPhone ;;
  }

  dimension: corrected_prev_auth_number {
    type: string
    sql: ${TABLE}.corrected_prevAuthNumber ;;
  }

  dimension: corrected_request_type_extension {
    type: string
    sql: ${TABLE}.corrected_requestTypeExtension ;;
  }

  dimension: corrected_request_type_initial {
    type: string
    sql: ${TABLE}.corrected_requestTypeInitial ;;
  }

  dimension: corrected_review_type_non_urgent {
    type: string
    sql: ${TABLE}.corrected_reviewTypeNonUrgent ;;
  }

  dimension: corrected_review_type_urgent {
    type: string
    sql: ${TABLE}.corrected_reviewTypeUrgent ;;
  }

  dimension: corrected_rp_contact_name {
    type: string
    sql: ${TABLE}.corrected_rpContactName ;;
  }

  dimension: corrected_rp_contact_phone {
    type: string
    sql: ${TABLE}.corrected_rpContactPhone ;;
  }

  dimension: corrected_rp_date {
    type: string
    sql: ${TABLE}.corrected_rpDate ;;
  }

  dimension: corrected_rp_fax {
    type: string
    sql: ${TABLE}.corrected_rpFax ;;
  }

  dimension: corrected_rp_name {
    type: string
    sql: ${TABLE}.corrected_rpName ;;
  }

  dimension: corrected_rp_npi {
    type: string
    sql: ${TABLE}.corrected_rpNPI ;;
  }

  dimension: corrected_rp_phone {
    type: string
    sql: ${TABLE}.corrected_rpPhone ;;
  }

  dimension: corrected_rp_specialty {
    type: string
    sql: ${TABLE}.corrected_rpSpecialty ;;
  }

  dimension: corrected_sp_fax {
    type: string
    sql: ${TABLE}.corrected_spFax ;;
  }

  dimension: corrected_sp_npi {
    type: string
    sql: ${TABLE}.corrected_spNPI ;;
  }

  dimension: corrected_sp_phone {
    type: string
    sql: ${TABLE}.corrected_spPhone ;;
  }

  dimension: corrected_sp_specialty {
    type: string
    sql: ${TABLE}.corrected_spSpecialty ;;
  }

  dimension: corrected_subscriber_name {
    type: string
    sql: ${TABLE}.corrected_subscriberName ;;
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

  measure: count {
    type: count
    drill_fields: [detail*]
  }

  # ----- Sets of fields for drilling ------
  set: detail {
    fields: [
      __subscriber_name,
      corrected_rp_contact_name,
      __rp_name,
      __rp_contact_name,
      __patient_name,
      corrected_patient_name,
      conf_subscriber_name,
      conf_rp_contact_name,
      __pcp_name,
      conf_rp_name,
      conf_pcp_name,
      conf_patient_name,
      corrected_subscriber_name,
      corrected_rp_name,
      corrected_pcp_name
    ]
  }
}
