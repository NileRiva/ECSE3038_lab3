from flask import Flask, request, jsonify
from datetime import datetime
from flask_pymongo import PyMongo
from marshmallow import Schema, fields, ValidationError
from bson.json_util import dumps
from json import loads
import os
from dotenv import load_dotenv
from functools import partial

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONG0_CONNECTION_STRING")
mongo = PyMongo(app)


def currdatetime():
    dt=datetime.now()
    currdatetimestr= dt.strftime("%d/%m/%Y, %H:%M:%S")
    return currdatetimestr

FAKEPROFDB = {} 
#FAKETANKDB = [] #Not needed right now
id_count = 0
profcount = 0
#CRUD

#CREATE PROFILE
@app.route("/profile", methods=["POST"])
def postprofile():
    username = request.json["username"]
    role = request.json["role"]
    color = request.json["color"] 
    user_profile = {
        "data":{
            "role": role,
            "color": color,
            "username": username,
            "last_updated": currdatetime(),
        },   
    }
    global FAKEPROFDB   
    #global profcount 
    #profcount+=1
    FAKEPROFDB = user_profile #cannot use .append() on dictionary 
    #FAKEPROFDB.update(user_profile: profcount)
    return jsonify(FAKEPROFDB)

#READ PROFILE
@app.route("/profile",methods = ["GET"])
def getprofiles():
    return jsonify(FAKEPROFDB)

#UPDATE PROFILE 
@app.route("/profile",methods = ["PATCH"])
def patchprofile():
    if "username" in  request.json:
        FAKEPROFDB["data"]["username"] = request.json["username"]
        FAKEPROFDB["data"]["last_updated"] = currdatetime()
    if "color" in request.json:
        FAKEPROFDB["data"]["color"] = request.json["color"]
        FAKEPROFDB["data"]["last_updated"] = currdatetime()
    if  "role" in request.json:
        FAKEPROFDB["data"]["role"] = request.json["role"]
        FAKEPROFDB["data"]["last_updated"] = currdatetime()    
    return jsonify(FAKEPROFDB)


#MAJOR CHANGES FOLLOW
class TankSchema(Schema):
    location = fields.String(required=True)
    lat = fields.Float(required=True)
    long = fields.Float(required=True)
    percentage_full = fields.Float(required=True)

@app.route("/data",methods = ["POST"])
def add_tank():    
    request_dict = request.json

    try:
        new_tank =  TankSchema().load(request_dict)
    except ValidationError as err:
        return (err.messages,400)

    tank_document = mongo.db.tanks.insert_one(new_tank)
    tank_id = tank_document.inserted_id
    tank = mongo.db.tanks.find_one({"_id":tank_id})
    tank_json = loads(dumps(tank))

    return jsonify(tank_json)

@app.route("/data",methods = ["GET"])
def get_tanks(): 
    tanks = mongo.db.tanks.find()
    tanks_list = loads(dumps(tanks))
    return jsonify(tanks_list)

@app.route("/data/<ObjectId:id>",methods = ["PATCH"])
def update_tank(id):
    request_dict = request.json

    try:
        tank_patch = TankSchema(partial=True).load(request_dict)
    except ValidationError as err:
        return(err.messages,400)

    mongo.db.tanks.update_one({"_id": id}, {"$set": request.json})
    tank = mongo.db.tanks.find_one({"_id":id})
    tank_json = loads(dumps(tank))
   
    return (tank_json)

@app.route("/data/<ObjectId:id>",methods=["DELETE"])
def delete_tank(id):

    result = mongo.db.tanks.delete_one({"_id":id})
    
    if result.deleted_count == 1:
        return {"success":True}
    else:
        return {"success":False},400
    

if __name__ == '__main__':
    app.run(
    debug=True, 
    port=3000,
    host="0.0.0.0")