from flask import Flask, jsonify, Response, request
import api
import typing
import json

app = Flask(__name__)


def _json_fail():
    return jsonify({"result": "fail"})


def _explode_and_fetch(type_label: str, fetch_function: typing.Callable[[], []]) -> Response:
    result_object = api.explode_type_label(type_label.strip())
    if result_object:
        fetch_json = fetch_function(**result_object)
        if fetch_json:
            result_json = {"result": fetch_json}
        else:
            result_json = {"result": "fail"}
        if result_json:
            return jsonify(result_json)
        else:
            return _json_fail()
    else:
        return _json_fail()


@app.route("/")
def hello():
    return "<h1>Universal Products JSON Database</h1><br>Please enter json data for a product<br><textarea cols='50'>"


@app.route("/get_type/<type_label>")
def get_type(type_label: str):
    return _explode_and_fetch(type_label, api.get_type)


@app.route("/get_children_types/<type_label>")
def get_children_types(type_label: str):
    return _explode_and_fetch(type_label, api.get_children_types)


@app.route("/get_parent_type/<type_label>")
def get_parent_types(type_label: str):
    return _explode_and_fetch(type_label, api.get_parent_type)


@app.route("/new_type/<new_type_name>/extends/<parent_type_label>")
def new_type(new_type_name: str, parent_type_label: str):
    result_object = api.explode_type_label(parent_type_label)
    if result_object:
        fetch_json = api.extend_type(new_type_name, result_object["meta_name"], result_object["meta_version"])
        if fetch_json:
            return jsonify({"result": fetch_json})
        else:
            return _json_fail()
    else:
        return _json_fail()


@app.route("/add_fields/<type_label>", methods=['POST'])
def add_fields(type_label: str):
    result_object = api.explode_type_label(type_label)
    if result_object:
        new_fields_list = json.loads(request.form["new_fields"])
        if new_fields_list:
            fetch_json = api.add_fields_to_type(result_object["meta_name"],
                                                result_object["meta_version"],
                                                new_fields_list)
            if fetch_json:
                return jsonify({"result": fetch_json})
            else:
                return _json_fail()
        else:
            return _json_fail()
    else:
        return _json_fail()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
