connection: "healthcare-demo"

# include all the views
include: "/views/**/*.view"

datagroup: cas_demo_default_datagroup {
  # sql_trigger: SELECT MAX(id) FROM etl_log;;
  max_cache_age: "1 hour"
}

persist_with: cas_demo_default_datagroup

explore: bsc_pa_forms {}

explore: prior_auth_form {}

explore: bsc_pa_form {}

explore: all_forms {}

explore: prior_auth_forms {}

explore: validation_table {}
