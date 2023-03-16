view: bsc_pa_forms {
  sql_table_name: `validation.BSC_PA_FORMS`
    ;;

  dimension: __beneficiary_address {
    type: string
    sql: ${TABLE}.__beneficiaryAddress ;;
  }

  dimension: __beneficiary_do_b {
    type: string
    sql: ${TABLE}.__beneficiaryDoB ;;
  }

  dimension: __beneficiary_language {
    type: string
    sql: ${TABLE}.__beneficiaryLanguage ;;
  }

  dimension: __beneficiary_name {
    type: string
    sql: ${TABLE}.__beneficiaryName ;;
  }

  dimension: __beneficiary_phone {
    type: string
    sql: ${TABLE}.__beneficiaryPhone ;;
  }

  dimension: __beneficiary_plan_number {
    type: string
    sql: ${TABLE}.__beneficiaryPlanNumber ;;
  }

  dimension: __beneficiary_state {
    type: string
    sql: ${TABLE}.__beneficiaryState ;;
  }

  dimension: __beneficiary_zip {
    type: string
    sql: ${TABLE}.__beneficiaryZip ;;
  }

  dimension: __date_last_authorized {
    type: string
    sql: ${TABLE}.__dateLastAuthorized ;;
  }

  dimension: __diag_code {
    type: string
    sql: ${TABLE}.__diagCode ;;
  }

  dimension: __diag_description {
    type: string
    sql: ${TABLE}.__diagDescription ;;
  }

  dimension: __ipa_responsibility {
    type: string
    sql: ${TABLE}.__ipaResponsibility ;;
  }

  dimension: __issurer_name {
    type: string
    sql: ${TABLE}.__issurerName ;;
  }

  dimension: __member_effective_date {
    type: string
    sql: ${TABLE}.__memberEffectiveDate ;;
  }

  dimension: __modification_fax {
    type: string
    sql: ${TABLE}.__modificationFax ;;
  }

  dimension: __prev_auth_number {
    type: string
    sql: ${TABLE}.__prevAuthNumber ;;
  }

  dimension: __proc_code {
    type: string
    sql: ${TABLE}.__procCode ;;
  }

  dimension: __proc_desc {
    type: string
    sql: ${TABLE}.__procDesc ;;
  }

  dimension: __referral_requested_by {
    type: string
    sql: ${TABLE}.__referralRequestedBy ;;
  }

  dimension: __retro_fax {
    type: string
    sql: ${TABLE}.__retroFax ;;
  }

  dimension: __routine_fax {
    type: string
    sql: ${TABLE}.__routineFax ;;
  }

  dimension: __rp_fax {
    type: string
    sql: ${TABLE}.__rpFax ;;
  }

  dimension: __rp_justification {
    type: string
    sql: ${TABLE}.__rpJustification ;;
  }

  dimension: __rp_name {
    type: string
    sql: ${TABLE}.__rpName ;;
  }

  dimension: __rp_npi {
    type: string
    sql: ${TABLE}.__rpNpi ;;
  }

  dimension: __rp_phone {
    type: string
    sql: ${TABLE}.__rpPhone ;;
  }

  dimension: __rp_sign {
    type: string
    sql: ${TABLE}.__rpSign ;;
  }

  dimension: __rp_specialty {
    type: string
    sql: ${TABLE}.__rpSpecialty ;;
  }

  dimension: __sp_address {
    type: string
    sql: ${TABLE}.__spAddress ;;
  }

  dimension: __sp_facility_name {
    type: string
    sql: ${TABLE}.__spFacilityName ;;
  }

  dimension: __sp_fax1 {
    type: string
    sql: ${TABLE}.__spFax1 ;;
  }

  dimension: __sp_fax2 {
    type: string
    sql: ${TABLE}.__spFax2 ;;
  }

  dimension: __sp_name {
    type: string
    sql: ${TABLE}.__spName ;;
  }

  dimension: __sp_npi {
    type: string
    sql: ${TABLE}.__spNpi ;;
  }

  dimension: __sp_phone2 {
    type: string
    sql: ${TABLE}.__spPhone2 ;;
  }

  dimension: __sp_request_date {
    type: string
    sql: ${TABLE}.__spRequestDate ;;
  }

  dimension: __urgent_fax {
    type: string
    sql: ${TABLE}.__urgentFax ;;
  }

  dimension: case_id {
    type: string
    sql: ${TABLE}.case_id ;;
  }

  dimension: conf_beneficiary_address {
    type: number
    sql: ${TABLE}.conf_beneficiaryAddress ;;
  }

  dimension: conf_beneficiary_do_b {
    type: number
    sql: ${TABLE}.conf_beneficiaryDoB ;;
  }

  dimension: conf_beneficiary_language {
    type: number
    sql: ${TABLE}.conf_beneficiaryLanguage ;;
  }

  dimension: conf_beneficiary_name {
    type: number
    sql: ${TABLE}.conf_beneficiaryName ;;
  }

  dimension: conf_beneficiary_phone {
    type: number
    sql: ${TABLE}.conf_beneficiaryPhone ;;
  }

  dimension: conf_beneficiary_plan_number {
    type: number
    sql: ${TABLE}.conf_beneficiaryPlanNumber ;;
  }

  dimension: conf_beneficiary_state {
    type: number
    sql: ${TABLE}.conf_beneficiaryState ;;
  }

  dimension: conf_beneficiary_zip {
    type: number
    sql: ${TABLE}.conf_beneficiaryZip ;;
  }

  dimension: conf_date_last_authorized {
    type: number
    sql: ${TABLE}.conf_dateLastAuthorized ;;
  }

  dimension: conf_diag_code {
    type: number
    sql: ${TABLE}.conf_diagCode ;;
  }

  dimension: conf_diag_description {
    type: number
    sql: ${TABLE}.conf_diagDescription ;;
  }

  dimension: conf_ipa_responsibility {
    type: number
    sql: ${TABLE}.conf_ipaResponsibility ;;
  }

  dimension: conf_issurer_name {
    type: number
    sql: ${TABLE}.conf_issurerName ;;
  }

  dimension: conf_member_effective_date {
    type: number
    sql: ${TABLE}.conf_memberEffectiveDate ;;
  }

  dimension: conf_modification_fax {
    type: number
    sql: ${TABLE}.conf_modificationFax ;;
  }

  dimension: conf_prev_auth_number {
    type: number
    sql: ${TABLE}.conf_prevAuthNumber ;;
  }

  dimension: conf_proc_code {
    type: number
    sql: ${TABLE}.conf_procCode ;;
  }

  dimension: conf_proc_desc {
    type: number
    sql: ${TABLE}.conf_procDesc ;;
  }

  dimension: conf_referral_requested_by {
    type: number
    sql: ${TABLE}.conf_referralRequestedBy ;;
  }

  dimension: conf_retro_fax {
    type: number
    sql: ${TABLE}.conf_retroFax ;;
  }

  dimension: conf_routine_fax {
    type: number
    sql: ${TABLE}.conf_routineFax ;;
  }

  dimension: conf_rp_fax {
    type: number
    sql: ${TABLE}.conf_rpFax ;;
  }

  dimension: conf_rp_justification {
    type: number
    sql: ${TABLE}.conf_rpJustification ;;
  }

  dimension: conf_rp_name {
    type: number
    sql: ${TABLE}.conf_rpName ;;
  }

  dimension: conf_rp_npi {
    type: number
    sql: ${TABLE}.conf_rpNpi ;;
  }

  dimension: conf_rp_phone {
    type: number
    sql: ${TABLE}.conf_rpPhone ;;
  }

  dimension: conf_rp_sign {
    type: number
    sql: ${TABLE}.conf_rpSign ;;
  }

  dimension: conf_rp_specialty {
    type: number
    sql: ${TABLE}.conf_rpSpecialty ;;
  }

  dimension: conf_sp_address {
    type: number
    sql: ${TABLE}.conf_spAddress ;;
  }

  dimension: conf_sp_facility_name {
    type: number
    sql: ${TABLE}.conf_spFacilityName ;;
  }

  dimension: conf_sp_fax1 {
    type: number
    sql: ${TABLE}.conf_spFax1 ;;
  }

  dimension: conf_sp_fax2 {
    type: number
    sql: ${TABLE}.conf_spFax2 ;;
  }

  dimension: conf_sp_name {
    type: number
    sql: ${TABLE}.conf_spName ;;
  }

  dimension: conf_sp_npi {
    type: number
    sql: ${TABLE}.conf_spNpi ;;
  }

  dimension: conf_sp_phone2 {
    type: number
    sql: ${TABLE}.conf_spPhone2 ;;
  }

  dimension: conf_sp_request_date {
    type: number
    sql: ${TABLE}.conf_spRequestDate ;;
  }

  dimension: conf_urgent_fax {
    type: number
    sql: ${TABLE}.conf_urgentFax ;;
  }

  dimension: corrected_beneficiary_address {
    type: string
    sql: ${TABLE}.corrected_beneficiaryAddress ;;
  }

  dimension: corrected_beneficiary_do_b {
    type: string
    sql: ${TABLE}.corrected_beneficiaryDoB ;;
  }

  dimension: corrected_beneficiary_language {
    type: string
    sql: ${TABLE}.corrected_beneficiaryLanguage ;;
  }

  dimension: corrected_beneficiary_name {
    type: string
    sql: ${TABLE}.corrected_beneficiaryName ;;
  }

  dimension: corrected_beneficiary_phone {
    type: string
    sql: ${TABLE}.corrected_beneficiaryPhone ;;
  }

  dimension: corrected_beneficiary_plan_number {
    type: string
    sql: ${TABLE}.corrected_beneficiaryPlanNumber ;;
  }

  dimension: corrected_beneficiary_state {
    type: string
    sql: ${TABLE}.corrected_beneficiaryState ;;
  }

  dimension: corrected_beneficiary_zip {
    type: string
    sql: ${TABLE}.corrected_beneficiaryZip ;;
  }

  dimension: corrected_date_last_authorized {
    type: string
    sql: ${TABLE}.corrected_dateLastAuthorized ;;
  }

  dimension: corrected_diag_code {
    type: string
    sql: ${TABLE}.corrected_diagCode ;;
  }

  dimension: corrected_diag_description {
    type: string
    sql: ${TABLE}.corrected_diagDescription ;;
  }

  dimension: corrected_ipa_responsibility {
    type: string
    sql: ${TABLE}.corrected_ipaResponsibility ;;
  }

  dimension: corrected_issurer_name {
    type: string
    sql: ${TABLE}.corrected_issurerName ;;
  }

  dimension: corrected_member_effective_date {
    type: string
    sql: ${TABLE}.corrected_memberEffectiveDate ;;
  }

  dimension: corrected_modification_fax {
    type: string
    sql: ${TABLE}.corrected_modificationFax ;;
  }

  dimension: corrected_prev_auth_number {
    type: string
    sql: ${TABLE}.corrected_prevAuthNumber ;;
  }

  dimension: corrected_proc_code {
    type: string
    sql: ${TABLE}.corrected_procCode ;;
  }

  dimension: corrected_proc_desc {
    type: string
    sql: ${TABLE}.corrected_procDesc ;;
  }

  dimension: corrected_referral_requested_by {
    type: string
    sql: ${TABLE}.corrected_referralRequestedBy ;;
  }

  dimension: corrected_retro_fax {
    type: string
    sql: ${TABLE}.corrected_retroFax ;;
  }

  dimension: corrected_routine_fax {
    type: string
    sql: ${TABLE}.corrected_routineFax ;;
  }

  dimension: corrected_rp_fax {
    type: string
    sql: ${TABLE}.corrected_rpFax ;;
  }

  dimension: corrected_rp_justification {
    type: string
    sql: ${TABLE}.corrected_rpJustification ;;
  }

  dimension: corrected_rp_name {
    type: string
    sql: ${TABLE}.corrected_rpName ;;
  }

  dimension: corrected_rp_npi {
    type: string
    sql: ${TABLE}.corrected_rpNpi ;;
  }

  dimension: corrected_rp_phone {
    type: string
    sql: ${TABLE}.corrected_rpPhone ;;
  }

  dimension: corrected_rp_sign {
    type: string
    sql: ${TABLE}.corrected_rpSign ;;
  }

  dimension: corrected_rp_specialty {
    type: string
    sql: ${TABLE}.corrected_rpSpecialty ;;
  }

  dimension: corrected_sp_address {
    type: string
    sql: ${TABLE}.corrected_spAddress ;;
  }

  dimension: corrected_sp_facility_name {
    type: string
    sql: ${TABLE}.corrected_spFacilityName ;;
  }

  dimension: corrected_sp_fax1 {
    type: string
    sql: ${TABLE}.corrected_spFax1 ;;
  }

  dimension: corrected_sp_fax2 {
    type: string
    sql: ${TABLE}.corrected_spFax2 ;;
  }

  dimension: corrected_sp_name {
    type: string
    sql: ${TABLE}.corrected_spName ;;
  }

  dimension: corrected_sp_npi {
    type: string
    sql: ${TABLE}.corrected_spNpi ;;
  }

  dimension: corrected_sp_phone2 {
    type: string
    sql: ${TABLE}.corrected_spPhone2 ;;
  }

  dimension: corrected_sp_request_date {
    type: string
    sql: ${TABLE}.corrected_spRequestDate ;;
  }

  dimension: corrected_urgent_fax {
    type: string
    sql: ${TABLE}.corrected_urgentFax ;;
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
      conf_issurer_name,
      __issurer_name,
      __rp_name,
      conf_sp_name,
      __beneficiary_name,
      conf_beneficiary_name,
      corrected_sp_name,
      corrected_sp_facility_name,
      conf_sp_facility_name,
      __sp_facility_name,
      corrected_issurer_name,
      conf_rp_name,
      __sp_name,
      corrected_beneficiary_name,
      corrected_rp_name
    ]
  }
}
