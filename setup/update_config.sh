(terraform output -json parser_config | python -m json.tool) > ../../../common/src/common/parser_config.json
(terraform output -json vertex_ai | python -m json.tool) > ../../../common/src/common/vertex_ai_config.json
