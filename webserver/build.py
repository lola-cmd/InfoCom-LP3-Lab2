from os import fdopen
from flask import Flask, render_template, request
from flask.json import jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import base64
import requests
import time
import redis
import pickle
import json
import os

app = Flask(__name__)
CORS(app)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'
SMS_USERNAME = "lo0875li-s@student.lu.se"
SMS_API_KEY = os.environ["SMS_API_KEY"]
APP_DOMAIN = os.environ["APP_DOMAIN"]

# change this so that you can connect to your redis server
# ===============================================
redis_server = redis.Redis(host="localhost", port=6379, decode_responses=True, charset="unicode_escape")
# ===============================================

# Translate OSM coordinate (longitude, latitude) to SVG coordinates (x,y).
# Input coords_osm is a tuple (longitude, latitude).
def translate(coords_osm):
    x_osm_lim = (13.143390664, 13.257501336)
    y_osm_lim = (55.678138854000004, 55.734680845999996)

    x_svg_lim = (212.155699, 968.644301)
    y_svg_lim = (103.68, 768.96)

    x_osm = coords_osm[0]
    y_osm = coords_osm[1]

    x_ratio = (x_svg_lim[1] - x_svg_lim[0]) / (x_osm_lim[1] - x_osm_lim[0])
    y_ratio = (y_svg_lim[1] - y_svg_lim[0]) / (y_osm_lim[1] - y_osm_lim[0])
    x_svg = x_ratio * (x_osm - x_osm_lim[0]) + x_svg_lim[0]
    y_svg = y_ratio * (y_osm_lim[1] - y_osm) + y_svg_lim[0]

    return x_svg, y_svg

@app.route('/', methods=['GET'])
def map():
    return render_template('index.html')

@app.route('/position', methods=['GET'])
def get_position():
    return render_template('position.html')

@app.route('/post_position', methods=['POST'])
def post_position():
    data =  json.loads(request.data.decode())
    lat = data["lat"]
    long = data["long"]
    print("GOT PHONE POSITION:", lat, long)
    redis_server.set("phone_position", json.dumps({ "lat": lat, "long": long }))
    return jsonify({ "success": True })

@app.route("/send_sms", methods=["POST"])
def send_sms():
    data =  json.loads(request.data.decode())
    phonenr = data["phonenr"]
    
    data = {
        "messages": [
            {
                "to": phonenr,
                "source": "sdk",
                "body": f"(SPARK DEMO)\n\nhttp://{APP_DOMAIN}/position.html\n\n(SPARK DEMO)"
            }
        ]
    }
    auth = base64.b64encode(f"{SMS_USERNAME}:{SMS_API_KEY}".encode()).decode()
    res = requests.post("https://rest.clicksend.com/v3/sms/send", headers={
        "Content-Type": "application/json",
        "Authorization": "Basic " + auth
    }, data=json.dumps(data))
    print(res)
    return jsonify({ "success": True, "res": res.text })

@app.route('/callout', methods=['GET'])
def callout():
    #=============================================================================================================================================
    # Get the information of all the drones from redis server and update the dictionary `drone_dict' to create the response 
    # drone_dict should have the following format:
    # e.g if there are two drones in the system with IDs: DRONE1 and DRONE2
    # drone_dict = {'DRONE_1':{'longitude': drone1_logitude_svg, 'latitude': drone1_logitude_svg, 'status': drone1_status},
    #               'DRONE_2': {'longitude': drone2_logitude_svg, 'latitude': drone2_logitude_svg, 'status': drone2_status}
    #              }
    # use function translate() to covert the coodirnates to svg coordinates
    #=============================================================================================================================================
    
    all_keys = redis_server.keys()
    return_dict = { "drones": {} }
    
    for key in all_keys:
        if(key == "phone_position"):
            continue

        obj = json.loads(redis_server.get(key))
        svg_coords = translate([obj["long"], obj["lat"]])
        print(obj, svg_coords)
        
        new_obj = {
            "longitude":svg_coords[0],
            "latitude": svg_coords[1],
            "status": obj["status"]
        }
        
        return_dict["drones"][key] = new_obj

    if(redis_server.get("phone_position")):
        phone_coords = json.loads(redis_server.get("phone_position"))
        svg_coords = translate([phone_coords["long"], phone_coords["lat"]])
        print(phone_coords, svg_coords)
        return_dict["phone_svg"] = { "x": svg_coords[0], "y": svg_coords[1] }
        return_dict["phone_latlong"] = { "lat": phone_coords["lat"], "long": phone_coords["long"] }
    
    return jsonify(return_dict)

if __name__ == "__main__":
    redis_server.delete("phone_position")
    app.run(debug=True, host='0.0.0.0', port='80')
