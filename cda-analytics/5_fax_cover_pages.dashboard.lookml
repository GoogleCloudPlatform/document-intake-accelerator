- dashboard: 5_fax_cover_pages
  title: 5_Fax Cover Pages
  layout: newspaper
  preferred_viewer: dashboards-next
  description: ''
  preferred_slug: GxjzSjG94vYz4a2Xdbevzz
  elements:
  - title: FAX Cover Pages
    name: FAX Cover Pages
    model: healthcare_demo_prior_auth_forms
    explore: all_forms
    type: looker_grid
    fields: [all_forms.timestamp_date, all_forms.case_id, all_forms.form]
    filters:
      all_forms.document_class: '"fax_cover_page"'
    sorts: [all_forms.case_id desc]
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
    show_sql_query_menu_options: false
    show_totals: true
    show_row_totals: true
    truncate_header: false
    series_column_widths:
      all_forms.case_id: 267
      all_forms.document_class: 123
      all_forms.uid: 222
      all_forms.gcs_doc_path: 776
      all_forms.timestamp_date: 116
      all_forms.form: 153
    listen: {}
    row: 0
    col: 8
    width: 8
    height: 10
  - title: Total PA Forms
    name: Total PA Forms
    model: healthcare_demo_prior_auth_forms
    explore: all_forms
    type: single_value
    fields: [all_forms.count_of_fax_cover_page]
    limit: 500
    column_limit: 50
    dynamic_fields: [{measure: count_of_uid, based_on: all_forms.uid, expression: '',
        label: Count of Uid, type: count_distinct, _kind_hint: measure, _type_hint: number}]
    custom_color_enabled: true
    show_single_value_title: true
    show_comparison: false
    comparison_type: value
    comparison_reverse_colors: false
    show_comparison_label: true
    enable_conditional_formatting: false
    conditional_formatting_include_totals: false
    conditional_formatting_include_nulls: false
    custom_color: "#F9AB00"
    single_value_title: FAX Cover Pages
    series_types: {}
    defaults_version: 1
    hidden_pivots: {}
    listen: {}
    row: 0
    col: 0
    width: 8
    height: 4
  - title: Fax Cover Page by Date
    name: Fax Cover Page by Date
    model: healthcare_demo_prior_auth_forms
    explore: all_forms
    type: looker_column
    fields: [all_forms.timestamp_date, all_forms.count_of_fax_cover_page]
    fill_fields: [all_forms.timestamp_date]
    sorts: [all_forms.timestamp_date desc]
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
    series_colors:
      all_forms.count_of_fax_cover_page: "#F9AB00"
    defaults_version: 1
    listen: {}
    row: 4
    col: 0
    width: 8
    height: 6
