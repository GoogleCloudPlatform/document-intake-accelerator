import os
import re
import json


def pattern_based_entities(parser_data):

    text = parser_data["text"]

    # pattern_1 = re.compile(r"SEX:?\s([A-Z])")

    pattern = re.compile(r"SEX.*?(?<!\w)(F|M)(?!\w)", flags=re.DOTALL)

    matched_text = re.search(pattern, text)

    if matched_text:
        # print(matched_text)
        sex = matched_text.group(1)
    else:
        sex = "T"
    print(sex)
    return sex

def default_entities_extraction(entity_dict, parser_entities, default_entities):

    for each_entity in parser_entities:
        key, val, confidence = each_entity.get("type", ""), each_entity.get("mentionText", ""), round(each_entity.get("confidence", 0), 2)
        if key in default_entities:
            entity_dict[key] = {"text": val, "confidence": confidence}

    return entity_dict



def derived_entities_extraction(entity_dict, parser_data, derived_entities):

    name_text = (entity_dict["Given Names"]["text"] + " " + entity_dict["Family Name"]["text"]).strip()
    name_confidence = round((entity_dict["Given Names"]["confidence"] + entity_dict["Family Name"]["confidence"])/2, 2)
    entity_dict["Name"] = {"text": name_text, "confience": name_confidence}

    sex = pattern_based_entities(parser_data)

    entity_dict["Sex"] = {"text": sex, "confidence": 1}

    return entity_dict

def entities_extraction(parser_data, required_entities):

    # Read the entities from the processor

    parser_entities = parser_data["entities"]

    default_entities = required_entities["default_entities"]
    derived_entities = required_entities.get("derived_entities")

    temp_dict = {"text": "", "confidence": 0}

    entity_dict = {each_entity: temp_dict for each_entity in default_entities}

    default_entities_extraction(entity_dict, parser_entities, default_entities)

    # only for DL, make it add for new parsers
    if derived_entities:
        for k in derived_entities.keys():
            entity_dict.update({k: temp_dict})

        derived_entities_extraction(entity_dict, parser_data, derived_entities)

    """
    for each_entity in parser_entities:
        key, val, confidence = each_entity.get("type", ""), each_entity.get("mentionText", ""), round(each_entity.get("confidence", 0), 2)
        if key in required_entities:
            entity_dict[key] = {"text": val, "confidence": confidence}

    name_text = (entity_dict["Given Names"]["text"] + " " + entity_dict["Family Name"]["text"]).strip()
    name_confidence = round((entity_dict["Given Names"]["confidence"] + entity_dict["Family Name"]["confidence"])/2, 2)
    entity_dict["Name"] = {"text": name_text, "confience": name_confidence}

    sex = pattern_based_entities(parser_data)

    entity_dict["Sex"] = {"text": sex, "confidence": 1}
    """

    return entity_dict

def get_text(doc_element: dict, document: dict):

    """
    Document AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
    """

    response = ""

    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    return response



if __name__=="__main__":
    parser_json = "utility-docs/parser-json/without-noisy"
    extracted_entities = "utility-docs/extracted-entities/without-noisy"

    required_entities =  {
        "default_entities": ["Family Name", "Given Names", "Document Id", "Expiration Date", "Date Of Birth",
                             "Issue Date",
                             "Address"],
        "derived_entities": {"Name": {"rule": ["Given Names", "Family Name"]}, "Sex": {"rule": "pattern"}}
    }

    required_entities = {
        "default_entities": ["invoice_id", "invoice_date", "due_date", "receiver_name", "service_address",
                             "total_tax_amount",
                             "supplier_account_number"]
    }

    json_files = os.listdir(parser_json)

    for each_json in json_files:
        with open(os.path.join(parser_json, each_json), 'r') as j:
            data = json.loads(j.read())
            print(each_json)

            entity_dict = entities_extraction(data, required_entities)

            # save extracted entities json
            with open("{}.json".format(os.path.join(extracted_entities, each_json.split('.')[0])), "w") as outfile:
                json.dump(entity_dict, outfile, indent=4)

