from type_api import *
from type_api import _extend_type_helper

client = pymongo.MongoClient(settings.mongo_uri)
product_db = client.get_default_database()
pp = pprint.PrettyPrinter(indent=4)


def test_explode_type_label():
    assert explode_type_label("horror_v2_book_v1") == {'meta_name': 'horror_v2_book', 'meta_version': 1}
    assert explode_type_label("book_v345") == {'meta_name': 'book', 'meta_version': 345}
    assert explode_type_label("bookv345") is None


def test_explode_type_label_as_tuple():
    assert explode_type_label_as_tuple("horror_v2_book_v1") == ('horror_v2_book', 1)


def test_implode_type_label():
    assert implode_type_label("book", 1) == "book_v1"
    assert implode_type_label("horror_book", 45) == "horror_book_v45"


def test_generate_field():
    assert generate_field("test_field1", FieldType.STR) == {"test_field1": {"type": FieldType.STR.value,
                                                                            "desc": ""}}
    assert generate_field("test_field2", FieldType.INT, "Test Text") == {"test_field2": {"type": FieldType.INT.value,
                                                                                         "desc": "Test Text"}}


def test_get_type():
    assert get_type() is None
    assert get_type("") is None
    assert get_type(meta_name="", meta_version=2) is None
    assert get_type(meta_name="dummy text") is None


def test_get_parent_type():
    assert get_parent_type() == get_type("product", 1)
    assert get_parent_type("product", 1) == get_type("product", 1)
    assert get_parent_type("dummy_text", 42) is None


def test__extend_type_helper():
    test_parent_type_1 = {"meta": {"name": "product", "extends": "", "version": 1}}
    test_child_type_1 = {"meta": {"name": "book", "version": 4, "extends": ""},
                         "title": {"desc": "dummy text", "type": FieldType.STR.value}}
    test_generated_type_1 = {"meta": {"name": "book", "version": 4, "extends": {"name": "product", "version": 1}},
                             "title": {"desc": "dummy text", "type": FieldType.STR.value}}
    assert test_generated_type_1 == _extend_type_helper(test_child_type_1, test_parent_type_1)
    test_parent_type_2 = {"meta": {"name": "book", "version": 1, "extends": {"name": "product", "version": 1}},
                          "title": {"type": FieldType.STR.value, "desc": "Title of Book"}}
    test_child_type_2 = {"meta": {"name": "horror_book", "version": 1, "extends": {"name": "product", "version": 1}},
                         "title": {"type": FieldType.STR.value, "desc": "Title of Book"}}
    test_generated_type_2 = {"meta": {"name": "horror_book", "version": 1, "extends": {"name": "book", "version": 1}},
                             "title": {"type": FieldType.STR.value, "desc": "Title of Book"}}
    assert test_generated_type_2 == _extend_type_helper(test_child_type_2, test_parent_type_2)


def test_extend_type():
    assert extend_type() is None
    assert extend_type("dummy1", "dummy2") is None
    assert extend_type(meta_name="dummy1", parent_meta_version=2) is None


def test_add_fields_to_type():
    assert add_fields_to_type("dummy", 42, """{"dummy": {"desc": "dsfasd"}""") is None # sometimes dict passed as str, it should converted to dict
    assert add_fields_to_type(meta_version=42, new_field_dict="""{"dummy": {"desc": "dsfasd"}""") is None
