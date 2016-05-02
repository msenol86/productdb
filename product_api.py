import json
import type_api
import copy
import pymongo
import settings
from typing import Dict, Optional, Union, Tuple, Any


client = pymongo.MongoClient(settings.mongo_uri)
product_db = client.get_default_database()


def check_product_against_type(type_label: str, product_json: str) -> bool:
    product_dict = json.loads(product_json)
    type_name, type_version = type_api.explode_type_label_as_tuple(type_label)
    current_type_dict = type_api.get_type(type_name, type_version)
    return _check_helper_1(product_dict, type_name, type_version) and _check_helper_2(product_dict, current_type_dict) and _check_helper_3(product_dict, current_type_dict)


def _eliminate_meta_data_from_product_dict(product_dict: Dict[str, Any]):
    tmp_product_dict = copy.deepcopy(product_dict)
    del tmp_product_dict['type_name']
    del tmp_product_dict['type_version']
    return tmp_product_dict


def _eliminate_meta_data_from_type_dict(type_dict: Dict[str, Any]):
    tmp_type_dict = copy.deepcopy(type_dict)
    del tmp_type_dict['meta']
    return tmp_type_dict


test_type_1 = """{
  "author": {
    "type": "string",
    "desc": "Title of Book"
  },
  "title": {
    "type": "string",
    "desc": "Title of Book"
  },
  "meta": {
    "name": "book",
    "version": 3,
    "extends": {
      "name": "book",
      "version": 2
    }
  }
}"""
test_type_1 = test_type_1.strip()
test_product_1 = """
{"type_name": "book", "type_version": 3, "author": "Tolkien", "title": "Lord of the Rings"}
"""
test_product_1 = test_product_1.strip()


assert _eliminate_meta_data_from_product_dict(json.loads(test_product_1)) == {"author": "Tolkien", "title": "Lord of the Rings"}
assert _eliminate_meta_data_from_type_dict(json.loads(test_type_1)) == {"author": {"type": "string", "desc": "Title of Book" }, "title": {"type": "string", "desc": "Title of Book"}}


def _check_helper_1(product_dict: Dict[str, Any], type_name, type_version):
    """ Check meta data """
    if "type_name" in product_dict and "type_version" in product_dict:
        if product_dict["type_name"] == type_name and product_dict["type_version"] == type_version:
            return True
        else:
            return False
    else:
        return False


def _check_helper_2(product_dict: Dict[str, Any], type_dict: Dict[str, Any]):
    """ Check the fields exists """
    type_fields = [a_field_key for a_field_key in type_dict.keys() if a_field_key != 'meta']
    product_fields = [a_field_key for a_field_key in product_dict.keys() if (a_field_key != 'type_name' and a_field_key != "type_version")]
    return set(type_fields) == set(product_fields)


test_type_1 = """{
  "author": {
    "type": "string",
    "desc": "Title of Book"
  },
  "title": {
    "type": "string",
    "desc": "Title of Book"
  },
  "meta": {
    "name": "book",
    "version": 3,
    "extends": {
      "name": "book",
      "version": 2
    }
  }
}"""
test_type_1 = test_type_1.strip()
test_product_1 = """
{"type_name": "book", "type_version": 3, "author": "Tolkien", "title": "Lord of the Rings"}
"""
test_product_1 = test_product_1.strip()

assert _check_helper_2(json.loads(test_product_1), json.loads(test_type_1)) == True


def compare_field_type(field_value: Any, field_type_string):
    if field_type_string == type_api.FieldType.STR.value:
        return type(field_value) is str
    elif field_type_string == type_api.FieldType.INT.value:
        return type(field_value) is int

assert compare_field_type("Tolkien", type_api.FieldType.STR.value)
assert compare_field_type(1, type_api.FieldType.INT.value)
assert compare_field_type(1, type_api.FieldType.STR.value) == False


def _check_helper_3(product_dict, type_dict):
    """ Check the type of field values """
    product_dict = _eliminate_meta_data_from_product_dict(product_dict)
    type_dict = _eliminate_meta_data_from_type_dict(type_dict)
    return all(compare_field_type(product_field_value, type_dict[product_field_key]["type"]) for product_field_key, product_field_value in product_dict.items())


test_product_dict_1 = {"type_name": "book", "type_version": 3, "author": "Tolkien", "title": "Lord of the Rings"}
test_product_dict_2 = {"type_name": "book", "type_version": 3, "author": 12, "title": "Lord of the Rings"}

test_type_dict = {
    "author": {
        "type": "string",
        "desc": "Title of Book"
    },
    "title": {
        "type": "string",
        "desc": "Title of Book"
    },
    "meta": {
        "name": "book",
        "version": 3,
        "extends": {
            "name": "book",
            "version": 2
        }
    }
}

assert _check_helper_3(test_product_dict_1, test_type_dict)
assert _check_helper_3(test_product_dict_2, test_type_dict) == False


def insert_product(type_label: str, product_json: str) -> Optional[int]:
    if check_product_against_type(type_label, product_json):
        product_dict = json.load(product_json)
        insert_result = product_db.products.insert_one(product_dict)
        if insert_result.acknowledged:
            return int(str(insert_result.inserted_id))
        else:
            print("Product not added")
            return None
    else:
        print("Product not added")
        return None

