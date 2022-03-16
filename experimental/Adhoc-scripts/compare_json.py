import json
import pandas as pd


with open("/home/venkatakrishna/Documents/Q/projects/doc-ai-test/application-arizona/extracted-entities/without-noisy/Arizona3.json", "r") as inf1:
    arizona1 = json.loads(inf1.read())
    arizona1 = pd.DataFrame(arizona1)

with open("/home/venkatakrishna/Documents/Q/projects/doc-ai-test/application-arizona/extracted-entities/without-noisy/Arizona6.json", "r") as inf2:
    arizona2 = json.loads(inf2.read())
    arizona2 = pd.DataFrame(arizona2)

temp_df = pd.merge(arizona1, arizona2, how='inner', left_on='key', right_on='key')

temp_df.to_csv('/home/venkatakrishna/Documents/Q/projects/doc-ai-test/application-arizona/arizona-extraction.csv', index=False)

print('debug')

