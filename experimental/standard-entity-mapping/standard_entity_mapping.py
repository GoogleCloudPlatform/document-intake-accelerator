def standard_entity_mapping(parser_extracted_entity_json):
    """
    This function is used to map the standard entities to the parser extracted entities
    """

    # convert extracted json to pandas dataframe
    df_json = pd.DataFrame.from_dict(parser_extracted_entity_json)
    # read entity standardization csv
    entities_standardization_csv = pd.read_csv('Entity Standardization.csv')
    entities_standardization_csv.dropna(how='all', inplace=True)
    # Create a dictionary from the look up dataframe/excel which has the key col and the value col
    dict_lookup = dict(
        zip(entities_standardization_csv['entity'], entities_standardization_csv['standard_entity_name']))
    # Get all the entity (key column) from the json as a list
    key_list = list(df_json['entity'])

    # Iterate over the key list and check if the key is in the dictionary
    if all(i in dict_lookup for i in key_list):
        # Replace the value by creating a list by looking up the value and assign to json entity
        df_json['entity'] = [dict_lookup[item] for item in key_list]
        # convert datatype from object to int for column 'extraction_confidence'
        df_json['extraction_confidence'] = pd.to_numeric(df_json['extraction_confidence'], errors='coerce')

        # check if there is any repeated entity (many to one)
        if any(df_json.duplicated('entity')):
            # concatenation of same entities values
            df_conc = df_json.groupby('entity')['value'].apply(' '.join).reset_index()
            # average of extraction_confidence of same/repeated entities
            df_av = df_json.groupby(['entity', 'mannual_extraction'])[
                'extraction_confidence'].mean().reset_index().round(2)
            df_final = pd.merge(df_conc, df_av, on="entity", how="inner")

            def is_digit(s):
                """Return True if all characters in the string are digits or space characters."""
                return s.replace(' ', '').isdigit()  # remove spaces

            for i in range(len(df_final)):
                # check if the value is digit and have more than one space between digits for "DOB" format entities
                if (is_digit(df_final.loc[i, "value"]) == True) & (df_final.loc[i, "value"].count(" ") > 1):
                    # replace ' ' with '/' for "DOB" format entities
                    add_delimiter_date = df_final.loc[i, 'value'].replace(' ', '/')
                    df_final.loc[i, 'value'] = add_delimiter_date
                    entities_extraction_dict = df_final.reset_index().to_dict(orient='records')
                    extracted_entities_final_json = [{k: v for k, v in d.items() if k != 'index'} for d in
                                                     entities_extraction_dict]
                    return extracted_entities_final_json
                else:
                    entities_extraction_dict = df_final.reset_index().to_dict(orient='records')
                    extracted_entities_final_json = [{k: v for k, v in d.items() if k != 'index'} for d in
                                                     entities_extraction_dict]
                    return extracted_entities_final_json
        else:
            entities_extraction_dict = df_json.reset_index().to_dict(orient='records')
            extracted_entities_final_json = [{k: v for k, v in d.items() if k != 'index'} for d in
                                             entities_extraction_dict]
            return extracted_entities_final_json

    else:

        # if the json key (entity) is not in the dictionary (excel), return the json entity as it is
        json_uncommon_key = [element for element in key_list if element not in dict_lookup]
        df_json_uncommon = df_json[df_json['entity'] == json_uncommon_key[0]]
        df_json.drop(df_json[df_json['entity'] == json_uncommon_key[0]].index, inplace=True)
        key_list.remove(json_uncommon_key[0])
        # Replace the value by creating a list by looking up the value and assign to json entity
        df_json['entity'] = [dict_lookup[item] for item in key_list]
        # convert datatype from object to int for column 'extraction_confidence'
        df_json['extraction_confidence'] = pd.to_numeric(df_json['extraction_confidence'], errors='coerce')

        # check if there is any repeated entity (many to one)
        if any(df_json.duplicated('entity')):
            # concatenation of same entities value
            df_conc = df_json.groupby('entity')['value'].apply(' '.join).reset_index()
            # average of extraction_confidence of same entities
            df_av = df_json.groupby(['entity', 'mannual_extraction'])[
                'extraction_confidence'].mean().reset_index().round(2)
            df_final = pd.merge(df_conc, df_av, on="entity", how="inner")
            df_final = df_final.append(df_json_uncommon, ignore_index=True)

            def is_digit(s):
                """Return True if all characters in the string are digits or space characters."""
                return s.replace(' ', '').isdigit()  # remove spaces

            for i in range(len(df_final)):
                # check if the value is digit and have more than one space between digits for "DOB" format entities
                if (is_digit(df_final.loc[i, "value"]) == True) & (df_final.loc[i, "value"].count(" ") > 1):
                    # replace ' ' with '/' for "DOB" format entities
                    add_delimiter_date = df_final.loc[i, 'value'].replace(' ', '/')
                    df_final.loc[i, 'value'] = add_delimiter_date
                    entities_extraction_dict = df_final.reset_index().to_dict(orient='records')
                    extracted_entities_final_json = [{k: v for k, v in d.items() if k != 'index'} for d in
                                                     entities_extraction_dict]
                    return extracted_entities_final_json
                else:
                    entities_extraction_dict = df_final.reset_index().to_dict(orient='records')
                    extracted_entities_final_json = [{k: v for k, v in d.items() if k != 'index'} for d in
                                                     entities_extraction_dict]
                    return extracted_entities_final_json
        else:
            entities_extraction_dict = df_json.reset_index().to_dict(orient='records')
            extracted_entities_final_json = [{k: v for k, v in d.items() if k != 'index'} for d in
                                             entities_extraction_dict]
            return extracted_entities_final_json
