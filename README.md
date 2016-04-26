# productdb
JSON Consumer Products Database System

A project intends to store data of all cosumer products in the world as JSON

Requirements:
* Python 3.4+
* Flask
* MongoDB 3

# Setup
1. Rename **settings.default.py** to **settings.py**
2. Create a database in Mongo and set **mongo_uri** in **settings.py** 

## Database Setup
1. Create a collection with name **types**
2. Create a collection with name **products**
3. Insert data below to **types** collection 
```javascript 
{"meta" : { "name" : "product", "extends" : "", "version" : 1 } }
```


# API Guide
## Avaiable Type API urls
### /get_type/\<type_label\>
Example: 
* /get_type/book_v1

Result: 
```javascript
{
  "result": {
    "meta": {
      "extends": {
        "name": "product",
        "version": 1
      },
      "name": "book",
      "version": 1
    }
  }
}
```
### /get_children_types/\<type_label\>
Example:
* /get_type/product_v1

Result:
```javascript
{
  "result": [
    {
      "meta": {
        "extends": {
          "name": "product",
          "version": 1
        },
        "name": "book",
        "version": 1
      }
    },
    {
      "meta": {
        "extends": {
          "name": "product",
          "version": 1
        },
        "name": "electronics",
        "version": 1
      }
    }
  ]
}
```

### /get_parent_type/\<type_label\>

Example: /get_parent_type/book_v1

```javascript
{
  "result": {
    "meta": {
      "extends": "",
      "name": "product",
      "version": 1
    }
  }
}
````
