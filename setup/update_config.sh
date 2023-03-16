#!/bin/bash
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
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PWD=$(pwd)
#(terraform output -json parser_config | python -m json.tool) > "${CONFIG_DIR}"/parser_config.json
#(terraform output -json vertex_ai | python -m json.tool) > ../../../common/src/common/vertex_ai_config.json


GLOBAL_CONFIG_FILE="config.json"
CONFIG_DIR="${DIR}/../common/src/common/config"
(terraform output -json parser_config | python -m json.tool) > "${CONFIG_DIR}/parser_config.json"

cd "${CONFIG_DIR}" || exit
jq -n 'reduce inputs as $s (.; (.[input_filename|rtrimstr(".json")]) += $s)'  parser_config.json  settings_config.json document_types_config.json docai_entity_mapping.json > "${GLOBAL_CONFIG_FILE}"
gsutil cp "${GLOBAL_CONFIG_FILE}" "gs://${TF_VAR_config_bucket}/config.json"

cd "$PWD" || exit