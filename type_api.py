from enum import Enum

import pymongo
import pprint
import json
import copy
import settings
import re
from typing import Dict, Optional, Union, Tuple, Any


class FieldType(Enum):
    STR = "string"
    INT = "integer"
    DEC = "decimal"

client = pymongo.MongoClient(settings.mongo_uri)
product_db = client.get_default_database()
pp = pprint.PrettyPrinter(indent=4)


def _purge_id(a_type):
    del a_type["_id"]
    return a_type


def explode_type_label(type_label: str) -> Optional[Dict[str, Union[str, int]]]:
    my_re = re.compile(r"^(?P<meta_name>\w+)_v(?P<meta_version>\d+)$")
    result_object = my_re.search(type_label)
    if result_object:
        result_group_dict = result_object.groupdict()
        result_group_dict["meta_version"] = int(result_group_dict["meta_version"])
        return result_group_dict
    else:
        return None


def explode_type_label_as_tuple(type_label: str) ->Optional[Tuple[str, int]]:
    """ return (meta_name, meta_version)"""
    exploded_dict = explode_type_label(type_label)
    if exploded_dict:
        return exploded_dict["meta_name"], exploded_dict["meta_version"]
    else:
        return None


def implode_type_label(type_meta_name:str, type_meta_version: int):
    return type_meta_name + "_v" + str(type_meta_version)


def generate_field(field_name: str, field_type: FieldType, desc: str="") -> Dict[str, str]:
    return {field_name: {"type": field_type.value, "desc": desc}}


def get_type(meta_name: str=None, meta_version: int=None) -> Optional[Dict[str, str]]:
    if not meta_name or not meta_version:
        return None
    elif meta_name.strip() == "":
        return None
    else:
        tmp_type = product_db.types.find_one({"meta.name": meta_name, "meta.version": meta_version})
        if tmp_type:
            _purge_id(tmp_type)
            return tmp_type
        else:
            return None


def get_summary(meta_name: Optional[str]=None,
                meta_version: Optional[int]=None,
                a_type: Optional[Dict[str, str]]=None) -> Optional[Dict[str, str]]:
    if a_type:
        tmp_type = get_type(a_type["meta"]["name"], int(a_type["meta"]["version"]))
    else:
        tmp_type = get_type(meta_name, meta_version)

    if tmp_type:
        shorten_type = {"meta": {"name": tmp_type["meta"]["name"],
                                 "version": int(tmp_type["meta"]["version"]),
                                 "extends": tmp_type["meta"]["extends"]}}
        return shorten_type
    else:
        return None


def get_parent_type(meta_name: Optional[str]=None, meta_version: Optional[int]=None) -> Optional[Dict[str, str]]:
    if not meta_name or not meta_version:
        return get_type("product", 1)
    elif meta_name == "product" and meta_version == 1:
        return get_type("product", 1)
    else:
        child_type = get_type(meta_name, meta_version)
        if child_type:
            return get_type(child_type["meta"]["extends"]["name"], int(child_type["meta"]["extends"]["version"]))
        else:
            return None


def _get_children_types_cur(meta_name: str, meta_version: int):
    children_cur = product_db.types.find({"meta.extends.name": meta_name, "meta.extends.version": int(meta_version)})
    return children_cur


def get_children_types(meta_name: str, meta_version: int):
    children_cur = _get_children_types_cur(meta_name, meta_version)
    return [get_type(child["meta"]["name"], int(child["meta"]["version"])) for child in children_cur]


def calculate_next_version_number(meta_name: str):
    tmp_cur = product_db.types.find({"meta.name": meta_name})
    version_numbers = [0]  # needed when there is no type available with meta_name
    for a_type in tmp_cur:
        version_numbers += [a_type["meta"]["version"]]
    max_version_number = int(max(version_numbers) + 1)
    return max_version_number


def _extend_type_helper(child_type: Dict[str, Any], parent_type: Dict[str, Any]):
    tmp_child_type = copy.deepcopy(child_type)
    tmp_child_type["meta"]["extends"] = {"name": parent_type["meta"]["name"],
                                         "version": int(parent_type["meta"]["version"])}
    return tmp_child_type


def extend_type(meta_name: str=None,
                parent_meta_name: str=None,
                parent_meta_version: int=None) -> Optional[Dict[str, Any]]:
    """This method should be used to define new types
    :param meta_name:
    :param parent_meta_name:
    :param parent_meta_version:
    :return: new created type or None if creation failed
    """
    if not meta_name or not parent_meta_name or not parent_meta_version:
        return None
    else:
        parent_type = get_type(parent_meta_name, parent_meta_version)
        version_number = calculate_next_version_number(meta_name)
        new_type = copy.deepcopy(parent_type)
        new_type["meta"]["name"] = meta_name
        new_type["meta"]["version"] = version_number
        generated_type = _extend_type_helper(new_type, parent_type)
        product_db.types.insert_one(generated_type)
        return _purge_id(generated_type)


def _add_fields_to_type_helper(old_type: Dict[str, str], new_field_dict: Dict[str, str]):
    old_type_2 = copy.deepcopy(old_type)
    tmp_old_version = int(old_type_2["meta"]["version"])
    old_type_2["meta"]["version"] = calculate_next_version_number(old_type_2["meta"]["name"])
    old_type_2.update(new_field_dict)
    old_type_2["meta"]["extends"]["name"] = old_type_2["meta"]["name"]
    old_type_2["meta"]["extends"]["version"] = tmp_old_version
    return old_type_2


def add_fields_to_type(meta_name: str=None, meta_version: int=None, new_field_dict: Dict[str, str]=None):
    """
    Adding fields to a type. This function does not alter the state of given type,
    it generates new type with a new version number
    :return: new generated type
    """
    if not meta_name or not meta_version or not new_field_dict:
        return None
    elif not isinstance(new_field_dict, dict):
        return None
    else:
        old_type = get_type(meta_name, meta_version)
        if old_type:
            updated_type = _add_fields_to_type_helper(old_type, new_field_dict)
            product_db.types.insert_one(updated_type)
            return get_type(updated_type["meta"]["name"], updated_type["meta"]["version"])
        else:
            return None
