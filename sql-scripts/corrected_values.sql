/*##################################################################################
# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###################################################################################*/

/*
 * Use Cases:
 * - Display All corrected values from HITL process
 */


WITH latest AS (
    SELECT *
    FROM `validation.validation_table` t
    WHERE timestamp = (SELECT MAX(timestamp) FROM `validation.validation_table` WHERE uid = t.uid ) /*and  timestamp > cast('2023-05-02T19:00:00' as datetime)*/
    ),
    flattened_1 AS (
SELECT *,
    JSON_VALUE(parent, "$.corrected_value") as corrected_value,
    JSON_VALUE(parent, "$.value") as value,
    CAST(JSON_VALUE(parent, "$.confidence") AS DECIMAL) as confidence,
    JSON_VALUE(parent, "$.name") as name,

FROM latest l
    CROSS JOIN UNNEST(JSON_QUERY_ARRAY(entities, "$")) parent
    )
SELECT * except (entities, parent, document_type) FROM flattened_1
WHERE corrected_value != ""
ORDER BY flattened_1.confidence ASC
