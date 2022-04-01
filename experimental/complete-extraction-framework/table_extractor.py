# pylint: disable=mixed-indentation
"""
Extract data from a table present in a form
"""

import pandas as pd
import json
from utils_functions import standard_entity_mapping

class TabelExtractor:
	"""
	Extract data from a table present in the form
	"""

	def __init__(self, json_path):

		self.json_path = json_path
		self.page_info = {}

		with open(json_path, encoding='utf-8') as f_obj:
			self.data = json.load(f_obj)

		self.table_attributes()

	def table_attributes(self):
		"""
		This function obtains information regarding all the tables.
		For ex. total tables, table header info, table row wise data in dataframe format
		"""

		table_info = {}
		if "pages" in self.data.keys():
			# Iterate over pages
			for pg_num, page in enumerate(self.data["pages"]):
				if "tables" in page.keys():

					# Iterate over tables
					for table_num, table in enumerate(page["tables"]):

						# extract header(columns)
						for _, hrow in enumerate(table["headerRows"]):
							table_data = [
								self.get_text(cell["layout"], self.data) for cell in hrow["cells"]
							]
							table_info[table_num] = {
							"columns": table_data, "tot_cols": len(table_data),
						  "header": bool(table_data),
							}
							# extract row wise data
							try:
								for _, row in enumerate(table["bodyRows"]):
									body_row_data = [
											get_text(cell["layout"], self.data) for cell in row["cells"]
									]
									table_data.append(body_row_data)
								table_info[table_num]['body_data'] = pd.DataFrame(table_data)
							except Exception as e:
								print(e)
								return "Table Emplty !!!"
				self.page_info[pg_num] = table_info
		else:
			return "No data in json"

	def extract_data(self, df, column_names: list, tot_rows: int = -1) -> list:
		"""
		Extract the data based on the columns

		Args:
				df (pandas): table dataframe
				column_names (list): list of column names
				tot_rows (int): max rows to be extracted
		Return:
			list of dict with row wise data for each columns
		"""
		if tot_rows < 0:
			tot_rows = len(df)-1

		out_df = df.iloc[:tot_rows, column_names]
		return out_df.to_dict('records')

	def extract_table_entities(self, table_entities, json_path):
		"""
		A forms table's data is extracted in the json format and is being
		filtered out based on the user input present.

		Args:
				table_entities (dict): user input to be used to filter out the json
				json_path (_type_): json file path for data extraction
		"""
		_, df = parse_table_parser_json(json_path)

		tot_rows = table_entities['max_rows']

		if table_entities.get('all_columns'):
			columns = df.columns

		elif table_entities.get('use_column_index'):
			all_columns = df.columns
			columns = [all_columns[i] for i in table_entities['column_index']]
		else:
			columns_list = table_entities.get('column_names')
			columns = [i['name'] for i in columns_list]

		return extract_data(df, columns, tot_rows)

	def get_text(self, el, data):
		"""Convert text offset indexes into text snippets."""
		text = ""
		# Span over the textSegments
		if "textAnchor" in el.keys():
			if "textSegments" in el["textAnchor"].keys():
				for segment in el["textAnchor"]["textSegments"]:
					# Check for startIndex. If not present = 0
					if "startIndex" in segment.keys():
							start_index = segment["startIndex"]
					else:
							start_index = 0
					# Check for endIndex. If not present = 0
					if "endIndex" in segment.keys():
							end_index = segment["endIndex"]
					else:
							end_index = 0
					text += data["text"][int(start_index) : int(end_index)]
		return text

	def get_entities(self, table_entities):
		header = table_entities["header"]

		out = []
		table_found = False

		# check header to find the table
		for _, page in self.page_info.items():
			for _, table in page.items():
				columns = table["columns"]
				# compare user provided header with table headers
				if header == columns:
					table_found = True
					break

		if not table_found:
			print("Table not found")
			return None

		# if table found extract the entities
		table_df = table["body_data"]

		for col_row in table_entities["entity_extraction"]:
			entity_val = table_df.iloc[col_row[1]][columns[col_row[0]]]
			data = {'entity': columns[col_row[0]],
							'value': entity_val,
							'row': col_row[1]
						 }
			out.append(data)


		return out

if __name__ == '__main__':
	t = TabelExtractor('/users/sumitvaise/Downloads/res_0.json')


