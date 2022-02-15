from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from marshmallow import Schema, fields
from bson.json_util import dumps
from json import loads
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONG0_CONNECTION_STRING")
mongo = PyMongo(app)

class FruitSchema(Schema):
    name = fields.String(required=True)
    sugar_content = fields.Integer(required=True)
    colour = fields.String(required=True)
    calories = fields.Integer(required=True)

#CREATE
@app.route("/fruit",methods=["POST"])
def add_new_fruit():
    request_dict = request.json
    new_fruit =  FruitSchema().load(request_dict)
    fruit_document =  mongo.db.Lab3.insert_one(new_fruit)
    fruit_id = fruit_document.inserted_id

    fruit = mongo.db.Lab3.find_one({"_id": fruit_id})
    fruit_json = loads(dumps(fruit))

    return jsonify(fruit_json)

#READ
@app.route("/fruit")
def get_fruits():
    fruits =mongo.db.Lab3.find()
    fruits_list = loads(dumps(fruits))
    return jsonify(fruits_list)

#UPDATE
@app.route("/fruits/<ObjectId:id>",methods=["PATCH"])
def update_fruit(id):
    mongo.db.Lab3.update_one({"_id":id},{"$set":request.data})
    fruit = mongo.db.Lab3.find_one({"_id": fruit_id})
    fruit_json = loads(dumps(fruit))
    return jsonify(fruit_json)

@app.route("/fruits/<ObjectId:id>",methods=["DELETE"])
def delete_fruit(id):
    result = mongo.db.Lab3.delete_one({"_id":id})

    if result.deleted_count == 1:
        return {"success":True}
    else:
        return {"success":False},400
if __name__ == '__main__':
    app.run(
        debug = True,
        port = 3001,
        host = "0.0.0.0"
    )