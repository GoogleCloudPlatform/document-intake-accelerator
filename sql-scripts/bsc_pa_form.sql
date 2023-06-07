WITH latest AS (
    SELECT *
    FROM `validation.validation_table` t
    WHERE timestamp = (SELECT MAX(timestamp) FROM `validation.validation_table` WHERE uid = t.uid )
    ),
    flattened_1 AS (
SELECT *,
    JSON_VALUE(parent, "$.corrected_value") as corrected_value,
    CAST(JSON_VALUE(parent, "$.confidence") AS DECIMAL) as confidence,
    JSON_VALUE(parent, "$.name") as name,
    JSON_VALUE(parent, "$.value") as value,
FROM latest l
    CROSS JOIN UNNEST(JSON_QUERY_ARRAY(entities, "$")) parent
    )
SELECT * except (entities, parent) FROM flattened_1
WHERE document_class = "pa_form_cda" or document_class = "bsc_pa_form"