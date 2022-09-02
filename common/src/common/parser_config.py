import json
import os

json_file = open(os.path.join(
    os.path.dirname(__file__), ".", "parser_config.json"))
PARSER_CONFIG_JSON = json.load(json_file)

assert PARSER_CONFIG_JSON, "Unable to locate 'parser_config.json'"
