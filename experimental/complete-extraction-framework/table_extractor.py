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
		self.tables_page_wise = {}

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
							columns = [" ".join(val.split()) for val in table_data]

							table_info[table_num] = {
							"columns": columns, "tot_cols": len(columns),
						  "header": bool(columns),
							}
							# extract row wise data
							row_datas = []
							try:
								for _, row in enumerate(table["bodyRows"]):
									body_row_data = [
											self.get_text(cell["layout"], self.data) for cell in row["cells"]
									]
									row_datas.append(body_row_data)
								table_info[table_num]['body_data'] = pd.DataFrame(row_datas, columns=columns)
							except Exception as e:
								print(e)
								return "Table Emplty !!!"
					self.tables_page_wise[pg_num] = table_info
		else:
			return "No data in json"

	# def extract_data(self, df, column_names: list, tot_rows: int = -1) -> list:
	# 	"""
	# 	Extract the data based on the columns

	# 	Args:
	# 			df (pandas): table dataframe
	# 			column_names (list): list of column names
	# 			tot_rows (int): max rows to be extracted
	# 	Return:
	# 		list of dict with row wise data for each columns
	# 	"""
	# 	if tot_rows < 0:
	# 		tot_rows = len(df)-1

	# 	out_df = df.iloc[:tot_rows, column_names]
	# 	return out_df.to_dict('records')

	# def extract_table_entities(self, table_entities, json_path):
	# 	"""
	# 	A forms table's data is extracted in the json format and is being
	# 	filtered out based on the user input present.

	# 	Args:
	# 			table_entities (dict): user input to be used to filter out the json
	# 			json_path (_type_): json file path for data extraction
	# 	"""
	# 	_, df = parse_table_parser_json(json_path)

	# 	tot_rows = table_entities['max_rows']

	# 	if table_entities.get('all_columns'):
	# 		columns = df.columns

	# 	elif table_entities.get('use_column_index'):
	# 		all_columns = df.columns
	# 		columns = [all_columns[i] for i in table_entities['column_index']]
	# 	else:
	# 		columns_list = table_entities.get('column_names')
	# 		columns = [i['name'] for i in columns_list]

	# 	return extract_data(df, columns, tot_rows)

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
		"""
		Extract data from table based on user specific inputs for a table.

		Args:
			table_entites (list): user specified table parameters

		Returns:
			out(list): extracted entities
		"""

		header = table_entities["header"]

		out = []
		table_found = False

		# check header to find the table
		for _, page in self.tables_page_wise.items():
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
		try:
			for col_row in table_entities["entity_extraction"]:
				row, col = col_row["row_no"], col_row["col"]
				entity_val = table_df.iloc[row][col]
				entity_val = " ".join(entity_val.split())
				data = {'entity': columns[col],
								'value': entity_val,
								'row': row
								}
				out.append(data)
		except:
			return out


		return out

if __name__ == '__main__':
	t = TabelExtractor('/users/sumitvaise/Downloads/res_0.json')
	table_entities = {'header': ['Date', 'Name of Employer/Company/ Union and Address (City, State and Zip Code)',
										 'Website URL or Name of person contacted',
										 'Method (In person, Internet, mail)',
										 'Type of work sought', 'Action taken on the date of contact'],
							      "entity_extraction": [{"col": 0, "row_no": 1},
																					{"col": 1, "row_no": 2},
																					{"col": 2, "row_no": 3},
																					{"col": 3, "row_no": 4},
																					{"col": 4, "row_no": 1},
																					{"col": 3, "row_no": 1},
																					{"col": 2, "row_no": 2},
																					{"col": 0, "row_no": 4},
                            							]
    }
	print(t.get_entities(table_entities))


