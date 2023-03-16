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
 * - Display All extracted entities (if there are multiple entries for the same uid, shows the latest entry)
 */


WITH latest AS (
    SELECT *
    FROM `validation_table` t
    WHERE timestamp = (SELECT MAX(timestamp) FROM `validation_table` WHERE uid = t.uid )
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

