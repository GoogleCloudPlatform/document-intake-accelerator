- dashboard: 2_texas_pa_forms
  title: 2_Texas PA Forms
  layout: newspaper
  preferred_viewer: dashboards-next
  description: ''
  preferred_slug: H1bNClmLzzylOnFnqmuaAr
  elements:
  - title: Texas PA Forms
    name: Texas PA Forms
    model: healthcare_demo_prior_auth_forms
    explore: prior_auth_forms
    type: single_value
    fields: [prior_auth_forms.count]
    filters:
      prior_auth_forms.timestamp_month: 12 months
    limit: 500
    column_limit: 50
    custom_color_enabled: true
    show_single_value_title: true
    show_comparison: false
    comparison_type: value
    comparison_reverse_colors: false
    show_comparison_label: true
    enable_conditional_formatting: true
    conditional_formatting_include_totals: false
    conditional_formatting_include_nulls: false
    color_application:
      collection_id: b43731d5-dc87-4a8e-b807-635bef3948e7
      palette_id: fb7bb53e-b77b-4ab6-8274-9d420d3d73f3
    custom_color: "#1A73E8"
    conditional_formatting: [{type: equal to, value: !!null '', background_color: "#1A73E8",
        font_color: !!null '', color_application: {collection_id: b43731d5-dc87-4a8e-b807-635bef3948e7,
          palette_id: 1e4d66b9-f066-4c33-b0b7-cc10b4810688}, bold: false, italic: false,
        strikethrough: false, fields: !!null ''}]
    series_types: {}
    defaults_version: 1
    up_color: "#3EB0D5"
    down_color: "#B1399E"
    total_color: "#C2DD67"
    show_value_labels: false
    show_x_axis_ticks: true
    show_x_axis_label: true
    x_axis_scale: auto
    show_y_axis_labels: true
    show_y_axis_ticks: true
    y_axis_gridlines: true
    listen: {}
    row: 0
    col: 0
    width: 10
    height: 2
  - title: Texas PA Forms
    name: Texas PA Forms (2)
    model: healthcare_demo_prior_auth_forms
    explore: prior_auth_forms
    type: looker_column
    fields: [prior_auth_forms.count, prior_auth_forms.timestamp_date]
    filters:
      prior_auth_forms.count: ">0"
    sorts: [prior_auth_forms.timestamp_date desc]
    limit: 500
    column_limit: 50
    x_axis_gridlines: false
    y_axis_gridlines: true
    show_view_names: false
    show_y_axis_labels: true
    show_y_axis_ticks: true
    y_axis_tick_density: default
    y_axis_tick_density_custom: 5
    show_x_axis_label: true
    show_x_axis_ticks: true
    y_axis_scale_mode: linear
    x_axis_reversed: true
    y_axis_reversed: false
    plot_size_by_field: false
    trellis: ''
    stacking: ''
    limit_displayed_rows: false
    legend_position: center
    point_style: none
    show_value_labels: true
    label_density: 25
    x_axis_scale: auto
    y_axis_combined: true
    ordering: none
    show_null_labels: false
    show_totals_labels: false
    show_silhouette: false
    totals_color: "#808080"
    x_axis_zoom: true
    y_axis_zoom: true
    series_types: {}
    defaults_version: 1
    show_row_numbers: true
    transpose: false
    truncate_text: true
    hide_totals: false
    hide_row_totals: false
    size_to_fit: true
    table_theme: white
    enable_conditional_formatting: false
    header_text_alignment: left
    header_font_size: 12
    rows_font_size: 12
    conditional_formatting_include_totals: false
    conditional_formatting_include_nulls: false
    title_hidden: true
    listen: {}
    row: 2
    col: 0
    width: 10
    height: 10
  - title: Texas PA Forms
    name: Texas PA Forms (3)
    model: healthcare_demo_prior_auth_forms
    explore: prior_auth_forms
    type: looker_grid
    fields: [prior_auth_forms.timestamp_date, prior_auth_forms.__member_id, prior_auth_forms.__patient_name,
      prior_auth_forms.form]
    sorts: [prior_auth_forms.timestamp_date desc]
    limit: 500
    column_limit: 50
    show_view_names: false
    show_row_numbers: true
    transpose: false
    truncate_text: true
    hide_totals: false
    hide_row_totals: false
    size_to_fit: true
    table_theme: white
    limit_displayed_rows: false
    enable_conditional_formatting: false
    header_text_alignment: left
    header_font_size: 12
    rows_font_size: 12
    conditional_formatting_include_totals: false
    conditional_formatting_include_nulls: false
    series_types: {}
    defaults_version: 1
    show_sql_query_menu_options: false
    show_totals: true
    show_row_totals: true
    truncate_header: false
    series_column_widths:
      prior_auth_forms.__rp_specialty: 209
      prior_auth_forms.__rp_contact_name: 214
      prior_auth_forms.__rp_npi: 146
      prior_auth_forms.gcs_doc_path: 703
      prior_auth_forms.__member_id: 126
      prior_auth_forms.__patient_name: 143
      prior_auth_forms.__pcp_name: 190
      prior_auth_forms.timestamp_date: 142
      prior_auth_forms.form: 138
    listen: {}
    row: 0
    col: 10
    width: 7
    height: 12
  - title: Texas PA Forms By Service Provider
    name: Texas PA Forms By Service Provider
    model: healthcare_demo_prior_auth_forms
    explore: prior_auth_forms
    type: looker_grid
    fields: [prior_auth_forms.count, prior_auth_forms.__sp_npi, prior_auth_forms.__sp_specialty]
    filters:
      prior_auth_forms.timestamp_month: 12 months
    sorts: [prior_auth_forms.count desc 0]
    limit: 500
    column_limit: 50
    show_view_names: false
    show_row_numbers: true
    transpose: false
    truncate_text: true
    hide_totals: false
    hide_row_totals: false
    size_to_fit: true
    table_theme: white
    limit_displayed_rows: false
    enable_conditional_formatting: false
    header_text_alignment: left
    header_font_size: 12
    rows_font_size: 12
    conditional_formatting_include_totals: false
    conditional_formatting_include_nulls: false
    series_types: {}
    defaults_version: 1
    show_sql_query_menu_options: false
    show_totals: true
    show_row_totals: true
    truncate_header: false
    series_column_widths:
      prior_auth_forms.count: 258
      prior_auth_forms.__sp_npi: 95
      prior_auth_forms.__sp_specialty: 166
    listen: {}
    row: 6
    col: 17
    width: 7
    height: 6
  - title: Texas PA Forms By Requesting Provider
    name: Texas PA Forms By Requesting Provider
    model: healthcare_demo_prior_auth_forms
    explore: prior_auth_forms
    type: looker_grid
    fields: [prior_auth_forms.count, prior_auth_forms.__rp_npi, prior_auth_forms.__rp_name]
    filters:
      prior_auth_forms.timestamp_month: 12 months
    sorts: [prior_auth_forms.count desc 0]
    limit: 500
    column_limit: 50
    show_view_names: false
    show_row_numbers: true
    transpose: false
    truncate_text: true
    hide_totals: false
    hide_row_totals: false
    size_to_fit: true
    table_theme: white
    limit_displayed_rows: false
    enable_conditional_formatting: false
    header_text_alignment: left
    header_font_size: 12
    rows_font_size: 12
    conditional_formatting_include_totals: false
    conditional_formatting_include_nulls: false
    series_types: {}
    defaults_version: 1
    show_sql_query_menu_options: false
    show_totals: true
    show_row_totals: true
    truncate_header: false
    series_column_widths:
      prior_auth_forms.__member_id: 358
      prior_auth_forms.__patient_name: 454
      prior_auth_forms.__rp_npi: 124
      prior_auth_forms.__rp_name: 140
      prior_auth_forms.count: 323
    listen: {}
    row: 0
    col: 17
    width: 7
    height: 6
