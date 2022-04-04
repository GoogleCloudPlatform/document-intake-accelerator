# pylint: disable=mixed-indentation
"""
Extract data from a table present in a form
"""

import os
import pandas as pd
import json
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

	def extract_table_body_without_header(self):
		"""
		find rows
		"""
		# for _, page in self.tables_page_wise.items():
		# 		for _, table in page.items():
		# 			table_df = table["body_data"]
		# 			try:
		# 				entity_val = table_df.iloc[row][col]
		# 				entity_val = " ".join(entity_val.split())
		# 				data = {'entity': columns[col],
		# 								'value': entity_val,
		# 								'row': row
		# 								}
		# 				out.append(data)
		pass

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
							# table_info = self.extract_table_body(table, table_info, table_num, columns)
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
								return "Table Empty !!!"
					self.tables_page_wise[pg_num] = table_info
		else:
			return "No data in json"

	def user_header_standard_entity_extraction(self, header):
		"""

		Args:
				header (_type_): _description_
		"""

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
			table_entities (list): user specified table parameters

		Returns:
			out(list): extracted entities
		"""

		if table_entities["isheader"]:
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
			entities_count = {}
			try:
				for col_row in table_entities["entity_extraction"]:
					row, col = col_row["row_no"], col_row["col"]
					if row >= len(table_df) or col >= len(columns):
						continue
					entity_name = columns[col]
					entity_val = table_df.iloc[row][col]
					entity_val = " ".join(entity_val.split())
					if entity_name in entities_count:
						entities_count[entity_name] += 1
					else:
						entities_count[entity_name] = 1
					standard_entity_name = f'{entity_name} (employer {entities_count[entity_name]})'


					data = {'entity': standard_entity_name,
									'value': entity_val,
									'row': row
									}
					out.append(data)
			except Exception as e:
				print(e)
			return out
		else:
			return self.extract_table_body_without_header()

if __name__ == '__main__':
	t = TabelExtractor('/users/sumitvaise/Downloads/res_0.json')
	table_entities = {'header': ['Date',
										'Name of Employer/Company/ Union and Address (City, State and Zip Code)',
										'Website URL or Name of person contacted',
										'Method (In person, Internet, mail)',
										'Type of work sought', 'Action taken on the date of contact'],
							      "entity_extraction": [{"col": 0, "row_no": 1},
																					{"col": 0, "row_no": 2},
																					{"col": 2, "row_no": 3},
																					{"col": 3, "row_no": 3},
																					{"col": 4, "row_no": 1},
																					{"col": 3, "row_no": 1},
																					{"col": 2, "row_no": 2},
																					{"col": 0, "row_no": 3},
                            							],
										"isheader": True
    }
	print(t.get_entities(table_entities))


