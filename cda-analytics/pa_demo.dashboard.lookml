- dashboard: prior_authorization_dashboard_
  title: 'Prior Authorization Dashboard '
  layout: newspaper
  preferred_viewer: dashboards-next
  description: ''
  preferred_slug: Ud3bqIIgbWrlQhyrtlhHSb
  elements:
  - title: BSC PA Request by Diagnosis
    name: BSC PA Request by Diagnosis
    model: healthcare_demo
    explore: bsc_pa_forms
    type: looker_grid
    fields: [bsc_pa_forms.__diag_code, bsc_pa_forms.count, bsc_pa_forms.__diag_description]
    filters:
      bsc_pa_forms.timestamp_date: 12 months
    sorts: [bsc_pa_forms.count desc 0]
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
    x_axis_gridlines: false
    y_axis_gridlines: true
    show_y_axis_labels: true
    show_y_axis_ticks: true
    y_axis_tick_density: default
    y_axis_tick_density_custom: 5
    show_x_axis_label: true
    show_x_axis_ticks: true
    y_axis_scale_mode: linear
    x_axis_reversed: false
    y_axis_reversed: false
    plot_size_by_field: false
    trellis: ''
    stacking: ''
    legend_position: center
    point_style: none
    show_value_labels: false
    label_density: 25
    x_axis_scale: auto
    y_axis_combined: true
    ordering: none
    show_null_labels: false
    show_totals_labels: false
    show_silhouette: false
    totals_color: "#808080"
    defaults_version: 1
    series_types: {}
    listen: {}
    row: 13
    col: 12
    width: 12
    height: 5
  - title: BSC PA Requests by Procedure
    name: BSC PA Requests by Procedure
    model: healthcare_demo
    explore: bsc_pa_forms
    type: looker_grid
    fields: [bsc_pa_forms.count, bsc_pa_forms.__proc_code, bsc_pa_forms.__proc_desc]
    filters:
      bsc_pa_forms.timestamp_date: 12 months
    sorts: [bsc_pa_forms.count desc 0]
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
    x_axis_gridlines: false
    y_axis_gridlines: true
    show_y_axis_labels: true
    show_y_axis_ticks: true
    y_axis_tick_density: default
    y_axis_tick_density_custom: 5
    show_x_axis_label: true
    show_x_axis_ticks: true
    y_axis_scale_mode: linear
    x_axis_reversed: false
    y_axis_reversed: false
    plot_size_by_field: false
    trellis: ''
    stacking: ''
    legend_position: center
    point_style: none
    show_value_labels: false
    label_density: 25
    x_axis_scale: auto
    y_axis_combined: true
    ordering: none
    show_null_labels: false
    show_totals_labels: false
    show_silhouette: false
    totals_color: "#808080"
    defaults_version: 1
    series_types: {}
    listen: {}
    row: 18
    col: 12
    width: 12
    height: 5
  - title: BSC PA Requests by Service Provider
    name: BSC PA Requests by Service Provider
    model: healthcare_demo
    explore: bsc_pa_forms
    type: looker_grid
    fields: [bsc_pa_forms.__sp_npi, bsc_pa_forms.count, bsc_pa_forms.__sp_name]
    sorts: [bsc_pa_forms.count desc 0]
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
    x_axis_gridlines: false
    y_axis_gridlines: true
    show_y_axis_labels: true
    show_y_axis_ticks: true
    y_axis_tick_density: default
    y_axis_tick_density_custom: 5
    show_x_axis_label: true
    show_x_axis_ticks: true
    y_axis_scale_mode: linear
    x_axis_reversed: false
    y_axis_reversed: false
    plot_size_by_field: false
    trellis: ''
    stacking: ''
    legend_position: center
    point_style: none
    show_value_labels: false
    label_density: 25
    x_axis_scale: auto
    y_axis_combined: true
    ordering: none
    show_null_labels: false
    show_totals_labels: false
    show_silhouette: false
    totals_color: "#808080"
    defaults_version: 1
    series_types: {}
    custom_color_enabled: true
    show_single_value_title: true
    show_comparison: false
    comparison_type: value
    comparison_reverse_colors: false
    show_comparison_label: true
    show_null_points: true
    interpolation: linear
    listen: {}
    row: 7
    col: 12
    width: 12
    height: 6
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
    width: 3
    height: 7
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
    x_axis_reversed: false
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
    listen: {}
    row: 0
    col: 3
    width: 9
    height: 7
  - title: BSC PA Forms
    name: BSC PA Forms
    model: healthcare_demo
    explore: bsc_pa_forms
    type: looker_column
    fields: [bsc_pa_forms.count, bsc_pa_forms.timestamp_date]
    filters:
      bsc_pa_forms.count: ">0"
    sorts: [bsc_pa_forms.timestamp_date desc]
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
    x_axis_reversed: false
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
    series_colors:
      bsc_pa_forms.count: "#12B5CB"
    defaults_version: 1
    row: 0
    col: 15
    width: 9
    height: 7
  - title: BSC PA Forms
    name: BSC PA Forms (2)
    model: healthcare_demo
    explore: bsc_pa_forms
    type: single_value
    fields: [bsc_pa_forms.count]
    filters:
      bsc_pa_forms.timestamp_month: 12 months
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
    custom_color: "#12B5CB"
    conditional_formatting: [{type: equal to, value: !!null '', background_color: "#1A73E8",
        font_color: !!null '', color_application: {collection_id: 7c56cc21-66e4-41c9-81ce-a60e1c3967b2,
          palette_id: 56d0c358-10a0-4fd6-aa0b-b117bef527ab}, bold: false, italic: false,
        strikethrough: false, fields: !!null ''}]
    series_types: {}
    defaults_version: 1
    listen: {}
    row: 0
    col: 12
    width: 3
    height: 7
  - title: Texas PA Form by Requesting Provider
    name: Texas PA Form by Requesting Provider
    model: healthcare_demo_prior_auth_forms
    explore: prior_auth_forms
    type: looker_grid
    fields: [prior_auth_forms.count, prior_auth_forms.__rp_npi, prior_auth_forms.__rp_contact_name,
      prior_auth_forms.__rp_specialty]
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
    listen: {}
    row: 7
    col: 0
    width: 12
    height: 6
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
    row: 18
    col: 0
    width: 12
    height: 5
  - title: Texas PA Forms By Patients
    name: Texas PA Forms By Patients
    model: healthcare_demo_prior_auth_forms
    explore: prior_auth_forms
    type: looker_grid
    fields: [prior_auth_forms.count, prior_auth_forms.__member_id, prior_auth_forms.__patient_name]
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
    row: 13
    col: 0
    width: 12
    height: 5
