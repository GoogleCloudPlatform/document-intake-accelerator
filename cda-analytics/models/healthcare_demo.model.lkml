connection: "healthcare-demo"

#Include views
include: "/cda-analytics/views/**/*.view"

#include all dashboards
include: "/cda-analytics/cas-report.dashboard.lookml"

datagroup: healthcare_demo_default_datagroup {
  # sql_trigger: SELECT MAX(id) FROM etl_log;;
  max_cache_age: "1 hour"
}

persist_with: healthcare_demo_default_datagroup

explore: bsc_pa_forms {}