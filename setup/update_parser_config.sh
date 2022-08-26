(terraform output -json parser_config | python -m json.tool) > ../../../common/src/common/parser_config.json
