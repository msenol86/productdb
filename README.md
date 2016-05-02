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
3. pip install -r requirements.txt

## Database Setup
1. Create a collection with name **types**
2. Create a collection with name **products**
3. Insert data below to **types** collection 
```javascript 
{"meta" : { "name" : "product", "extends" : "", "version" : 1 } }
```

