from flatten_json import flatten
import os
import random
import json
import pandas as pd

extracted_entities = "dl-docs/extracted-entities/without-noisy"

# read ip doc folder
extracted_jsons = os.listdir(extracted_entities)

list_jsons = []
for each_json in extracted_jsons:
    with open(os.path.join(extracted_entities, each_json)) as f:

        data = json.load(f)
        data["filename"] = each_json

        flat_json = flatten(data)
        list_jsons.append(flat_json)

df = pd.DataFrame(list_jsons)

df.to_csv("dl-docs/DL_entities_without_noisy-new.csv", index=False)

