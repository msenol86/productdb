import json
import type_api
from typing import Dict, Optional, Union, Tuple, Any


def check_product_against_type(type_label: str, product_json: str):
    product_dict = json.loads(product_json)
    type_name, type_version = type_api.explode_type_label_as_tuple(type_label)
    if _check_helper_1(product_dict, type_name, type_version):
        pass
    else:
        return False


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
