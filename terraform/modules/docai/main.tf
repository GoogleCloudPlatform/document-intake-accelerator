/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

resource "google_document_ai_processor" "processors" {
  location     = var.multiregion
  for_each     = var.processors
  display_name = each.key
  type         = each.value
}

output "parser_config" {
  value = {
    for k, processor in google_document_ai_processor.processors : processor.display_name => {
        location = var.multiregion
        parser_name = processor.display_name
        parser_type = processor.type
        processor_id = processor.id
    }
  }
}
