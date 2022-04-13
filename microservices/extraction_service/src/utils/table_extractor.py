# pylint: disable=mixed-indentation
"""
Extract data from a table present in a form
"""

import json
class TableExtractor:
	"""
	Extract data from a table present in the form
	"""

	def __init__(self, json_path):

		self.json_path = json_path
		# master_dict --> page_num > tables > table_num > table data
		self.master_dict = {}

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

				page_data = {}
				if "tables" in page.keys():

					# Iterate over tables
					for table_num, table in enumerate(page["tables"]):

						# extract header(columns)
						for _, hrow in enumerate(table["headerRows"]):
							header_row = [
								TableExtractor.get_text(cell["layout"], self.data) for cell in hrow["cells"]
							]
							columns = []
							for val, conf, cord in header_row:
								if val is None:
									columns.append(val, conf, cord)
								else:
									columns.append((" ".join(val.split()), conf, cord))
							table_data = {"headers": columns}
							col_data = {}
							try:
								for row_num, row in enumerate(table["bodyRows"]):
									row_data = [
											TableExtractor.get_text(cell["layout"], self.data) for cell in row["cells"]
									]
									for i_col in range(len(header_row)):
										entity_val, conf, coordinates = row_data[i_col]
										col_data[i_col] = {
											"value": entity_val,
											"extraction_confidence": conf,
											"key_coordinates": coordinates,
											"manual_extraction": False,
											"corrected_value": 0
										}
									table_data[row_num] = {"rows": col_data}

							except Exception as e:
								print(e)
								return "Table Empty !!!"

						page_data[table_num] = table_data
					self.master_dict[pg_num] = page_data
		else:
			return "No data in json"

	@staticmethod
	def get_text(el, data):
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
					cell_conf = el["confidence"]
					cell_coordinates = el["boundingPoly"]["normalizedVertices"]
		if text in ("", None):
			text = None
		return (text, cell_conf, cell_coordinates)

	@staticmethod
	def compare_lists(master_list, sub_list):
		"""Compare two list and return the avg match percentage

		Args:
				list1 (list): list with items
				list2 (list): list with items
		"""
		x = lambda x: x in master_list

		matched = list(filter(x, sub_list))
		return len(matched)/len(master_list)

	@staticmethod
	def get_table_using_header(page, inp_header):
		"""uses the page info to extract the table

		Args:
				page (dict): dict that contains a table info
				inp_header (list): list of column names to match with the header of a table
		"""

		for pg_num in page:
			for table_num in page[pg_num]:
				table_dict = page[pg_num][table_num]
				table_header = [val[0] for val in table_dict["headers"]]
				if TableExtractor.compare_lists(table_header, inp_header) >= 0.75:
					return table_dict, table_header
				else:
					continue

		return None

	def get_entities(self, table_entities):
		"""
		Extract data from table based on user specific inputs for a table.

		Args:
			table_entities (list): user specified table parameters

		Returns:
			out(list): extracted entities
		"""

		if table_entities["isheader"]:
			inp_header = table_entities["headers"]
			if isinstance(table_entities["table_num"], int):
				table_num = table_entities["table_num"]
			else:
				table_num = 0
			if isinstance(table_entities["page_num"], int):
				page_num = table_entities["page_num"]
			else:
				page_num = 0

			try:
				if table_num > 0 and page_num > 0:
					table_dict = self.master_dict[page_num][table_num]
					columns = [val[0] for val in table_dict["headers"]]
					if TableExtractor.compare_lists(columns, inp_header) < 0.75:
						return "Table does not match with the headers provided"


				# if no table and page info provided. Iterate over all the pages to find the table
				# based on header
				elif page_num == 0 and table_num == 0:
					table_dict, columns = TableExtractor.get_table_using_header(self.master_dict, inp_header)
				elif page_num > 0 and table_num == 0:
					if not page_num in self.master_dict:
						return "page not found"
					page_dict = self.master_dict[page_num]
					table_dict, columns = TableExtractor.get_table_using_header(page_dict, inp_header)
				else:
					return "Operation cannot be performed. Check your config"
			except Exception as e:
				print(e)
				return "Issue with table number or page number or table or page not found!!!"

			out = []

			for user_inp in table_entities["entity_extraction"]:
				try:
					entity_data = {}
					suffix, row, col = user_inp["entity_suffix"], user_inp["row_no"], user_inp["col"]
					row_dict = table_dict[row]["rows"]
					if suffix in (None, ""):
						suffix = ""
					entity_name = f"{columns[col]} {suffix}"
					entity_data = row_dict[col]
					entity_data["entity"] = entity_name

					out.append(entity_data)
				except Exception as e:
					print(e)
					continue
			return out
		else:
			return "No header present in the table. Table not extracted."

if __name__ == '__main__':
	t = TableExtractor('/users/sumitvaise/Downloads/res_0.json')
	headers = ['Date',
						'Name of Employer/Company/ Union and Address (City, State and Zip Code)',
						'Website URL or Name of person contacted',
						'Method (In person, Internet, mail)',
						'Type of work sought', 'Action taken on the date of contact']
	table_entities = {
      "isheader": True,
      # if table and page number is unknown mark the variables to 0
      "table_num": 0, "page_num": 15,
      "headers": ["Date", "Name of Employer/Company/ Union and Address (City, State and Zip Code)",
								 "Website URL or Name of person contacted",
								 "Method (In person, Internet, mail)",
								 "Type of work sought", "Action taken on the date of contact"],
                 # entity name will be constructed based on the col number provided
                 # for an employer
                 "entity_extraction": [
                  {"entity_suffix": f"(employer 1)", "col": 7, "row_no": 1},
                  {"entity_suffix": f"(employer 2)", "col": 0, "row_no": 2},
                  {"entity_suffix": f"(employer 1)", "col": 2, "row_no": 2},
                  {"entity_suffix": f"(employer 1)", "col": 3, "row_no": 1},
                  {"entity_suffix": f"(employer 1)", "col": 4, "row_no": 1},
                  {"entity_suffix": f"(employer 2)", "col": 3, "row_no": 2},
                  {"entity_suffix": f"(employer 2)", "col": 2, "row_no": 3},
                  {"entity_suffix": f"(employer 3)", "col": 0, "row_no": 3},
                ],
  }
	print(t.get_entities(table_entities))
	# standard_entity_mapping(out)

