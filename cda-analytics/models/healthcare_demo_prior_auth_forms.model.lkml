connection: "cda_engine_bigquery"

# include all the views
include: "/cda-analytics/views/*.view.lkml"

# include all views in the views/ folder in this project


#only need to include dashboard in one model, even if it uses multiple models
#include all dashboards
#include: "/*.dashboard"

# Datagroups define a caching policy for an Explore. To learn more,
# use the Quick Help panel on the right to see documentation.

datagroup: healthcare_demo_prior_auth_forms_default_datagroup {
  # sql_trigger: SELECT MAX(id) FROM etl_log;;
  max_cache_age: "1 hour"
}

persist_with: healthcare_demo_prior_auth_forms_default_datagroup

# Explores allow you to join together different views (database tables) based on the
# relationships between fields. By joining a view into an Explore, you make those
# fields available to users for data analysis.
# Explores should be purpose-built for specific use cases.

# To see the Explore you’re building, navigate to the Explore menu and select an Explore under "Healthcare Demo Prior Auth Forms"

# To create more sophisticated Explores that involve multiple views, you can use the join parameter.
# Typically, join parameters require that you define the join type, join relationship, and a sql_on clause.
# Each joined view also needs to define a primary key.

explore: prior_auth_forms {}
explore: all_forms {}
