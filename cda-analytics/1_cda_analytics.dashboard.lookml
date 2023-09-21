- dashboard: 1_cda_analytics
  title: 1_CDA Analytics
  layout: newspaper
  preferred_viewer: dashboards-next
  description: ''
  preferred_slug: Ud3bqIIgbWrlQhyrtlhHSb
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
    row: 5
    col: 0
    width: 4
    height: 2
  - title: BSC PA Forms
    name: BSC PA Forms
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
    row: 5
    col: 4
    width: 3
    height: 2
  - title: ''
    name: ''
    model: healthcare_demo_prior_auth_forms
    explore: all_forms
    type: looker_pie
    fields: [all_forms.document_class, count_of_uid]
    sorts: [count_of_uid desc 0]
    limit: 500
    column_limit: 50
    total: true
    dynamic_fields: [{measure: count_of_document_class, based_on: all_forms.document_class,
        expression: '', label: Count of Document Class, type: count_distinct, _kind_hint: measure,
        _type_hint: number}, {measure: count_of_uid, based_on: all_forms.uid, expression: '',
        label: Count of Uid, type: count_distinct, _kind_hint: measure, _type_hint: number}]
    value_labels: legend
    label_type: labPer
    inner_radius: 50
    color_application:
      collection_id: 7c56cc21-66e4-41c9-81ce-a60e1c3967b2
      palette_id: 5d189dfc-4f46-46f3-822b-bfb0b61777b1
      options:
        steps: 5
    series_colors:
      pa_form_cda: "#12B5CB"
      pa_form_texas: "#1A73E8"
    series_labels:
      pa_form_cda: BSC PA Forms
      pa_form_texas: Texas PA Forms
      fax_cover_page: FAX Coversheet
      generic_form: Generic Form
      health_intake_form: Health Intake Form
    series_types: {}
    custom_color_enabled: true
    show_single_value_title: true
    show_comparison: false
    comparison_type: value
    comparison_reverse_colors: false
    show_comparison_label: true
    enable_conditional_formatting: false
    conditional_formatting_include_totals: false
    conditional_formatting_include_nulls: false
    defaults_version: 1
    hidden_pivots: {}
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
    show_value_labels: false
    label_density: 25
    x_axis_scale: auto
    y_axis_combined: true
    ordering: none
    show_null_labels: false
    show_totals_labels: false
    show_silhouette: false
    totals_color: "#808080"
    show_null_points: true
    interpolation: linear
    title_hidden: true
    listen: {}
    row: 0
    col: 4
    width: 9
    height: 5
  - title: All Forms
    name: All Forms
    model: healthcare_demo_prior_auth_forms
    explore: all_forms
    type: looker_grid
    fields: [all_forms.timestamp_date, all_forms.case_id, all_forms.form]
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
    col: 13
    width: 11
    height: 7
  - title: Total PA Forms
    name: Total PA Forms
    model: healthcare_demo_prior_auth_forms
    explore: all_forms
    type: single_value
    fields: [count_of_uid]
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
    series_types: {}
    defaults_version: 1
    hidden_pivots: {}
    row: 0
    col: 0
    width: 4
    height: 5
  - title: All Forms
    name: All Forms (2)
    model: healthcare_demo_prior_auth_forms
    explore: all_forms
    type: looker_column
    fields: [all_forms.timestamp_date, count_of_uid]
    fill_fields: [all_forms.timestamp_date]
    sorts: [all_forms.timestamp_date desc]
    limit: 500
    column_limit: 50
    dynamic_fields: [{measure: count_of_case_id, based_on: all_forms.case_id, expression: '',
        label: Count of Case ID, type: count_distinct, _kind_hint: measure, _type_hint: number},
      {measure: count_of_uid, based_on: all_forms.uid, expression: '', label: Count
          of Uid, type: count_distinct, _kind_hint: measure, _type_hint: number}]
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
      count_of_uid: "#A8A116"
    defaults_version: 1
    hidden_pivots: {}
    listen: {}
    row: 7
    col: 0
    width: 13
    height: 7
  - title: Medical Forms
    name: Medical Forms
    model: healthcare_demo_prior_auth_forms
    explore: all_forms
    type: single_value
    fields: [all_forms.count_of_medical_forms]
    limit: 500
    column_limit: 50
    dynamic_fields: [{category: measure, expression: '', label: Count of Uid, based_on: all_forms.uid,
        _kind_hint: measure, measure: count_of_uid, type: count_distinct, _type_hint: number,
        filters: {all_forms.document_class: '"generic_form","health_intake_form"'}}]
    custom_color_enabled: true
    show_single_value_title: true
    show_comparison: false
    comparison_type: value
    comparison_reverse_colors: false
    show_comparison_label: true
    enable_conditional_formatting: false
    conditional_formatting_include_totals: false
    conditional_formatting_include_nulls: false
    custom_color: "#E52592"
    hidden_pivots: {}
    series_types: {}
    defaults_version: 1
    listen: {}
    row: 5
    col: 7
    width: 3
    height: 2
  - title: Fax Cover Page
    name: Fax Cover Page
    model: healthcare_demo_prior_auth_forms
    explore: all_forms
    type: single_value
    fields: [all_forms.count_of_fax_cover_page]
    limit: 500
    column_limit: 50
    dynamic_fields: [{category: measure, expression: '', label: Count of Uid, based_on: all_forms.uid,
        _kind_hint: measure, measure: count_of_uid, type: count_distinct, _type_hint: number,
        filters: {all_forms.document_class: '"fax_cover_page"'}}]
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
    hidden_pivots: {}
    series_types: {}
    defaults_version: 1
    listen: {}
    row: 5
    col: 10
    width: 3
    height: 2
  - title: Texas PA Forms by State
    name: Texas PA Forms by State
    model: healthcare_demo_prior_auth_forms
    explore: all_forms
    type: looker_google_map
    fields: [count_of_uid, all_forms.value]
    filters:
      all_forms.name: "%beneficiaryState%,%State%"
    sorts: [count_of_uid desc 0]
    limit: 500
    column_limit: 50
    dynamic_fields: [{measure: count_of_uid, based_on: all_forms.uid, expression: '',
        label: Count of Uid, type: count_distinct, _kind_hint: measure, _type_hint: number}]
    hidden_fields: []
    hidden_points_if_no: []
    series_labels: {}
    show_view_names: true
    hidden_pivots: {}
    custom_color_enabled: true
    show_single_value_title: true
    show_comparison: false
    comparison_type: value
    comparison_reverse_colors: false
    show_comparison_label: true
    enable_conditional_formatting: false
    conditional_formatting_include_totals: false
    conditional_formatting_include_nulls: false
    defaults_version: 0
    series_types: {}
    row: 7
    col: 13
    width: 11
    height: 7
