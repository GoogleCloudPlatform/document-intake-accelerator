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
