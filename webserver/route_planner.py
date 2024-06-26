from cmath import pi
from flask import Flask, request, render_template, jsonify
from flask.globals import current_app 
from geopy.geocoders import Nominatim
from flask_cors import CORS
import redis
import json
import requests

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

# change this to connect to your redis server
# ===============================================
redis_server = redis.Redis(host="localhost", port=6379, decode_responses=True, charset="unicode_escape")
# ===============================================

geolocator = Nominatim(user_agent="my_request")
region = ", Lund, Skåne, Sweden"

# Example to send coords as request to the drone
def send_request(drone_url, coords):
    with requests.Session() as session:
        resp = session.post(drone_url, json=coords)

def planner(from_location, to_location):
    print(from_location, to_location)

    try:
        if to_location is None:
            message = 'Destination address not found, please input a correct address'
            return message
        else:
            # If the coodinates are found by Nominatim, the coords will need to be sent the a drone that is available
            coords = { 'from': (from_location["longitude"], from_location["latitude"]), 'to': (to_location["longitude"], to_location["latitude"]), }
            # if from_location is not None:
                
            # else:
            #     coords = { 'to': (to_location["longitude"], to_location["latitude"]), }
            # ======================================================================
            # Here you need to find a drone that is availale from the database. You need to check the status of the drone, there are two status, 'busy' or 'idle', only 'idle' drone is available and can be sent the coords to run delivery
            # 1. Find avialable drone in the database (Hint: Check keys in RedisServer)
            # if no drone is availble:
            message = 'No available drone, try later'
            
            all_keys = redis_server.keys()
            
            idle_drone = None
            
            for key in all_keys:
                if(key == "phone_position"):
                    continue

                obj = json.loads(redis_server.get(key))
                print(obj)
                if obj["status"] == "idle":
                    idle_drone = obj
                    break
                
            if idle_drone:
                # print(idle_drone)
                # if from_location is None:
                #     coords["to"] = (float(idle_drone["long"]), float(idle_drone["lat"]))
                print("COORDS ARE: ", coords)
                # else:
                    # 2. Get the IP of available drone, 
                DRONE_URL = 'http://' + idle_drone["ip"]+':5004'
                    # 3. Send coords to the URL of available drone
                send_request(DRONE_URL, coords)
                message = 'Got address and sent request to the drone'
    except Exception as e:
        message = str(e)
        return message
        
    return message
        # ======================================================================

@app.route("/phone_planner", methods=["POST"])
def phone_planner():
    locations =  json.loads(request.data.decode())
    return planner({ "latitude": locations["lat"], "longitude": locations["long"] }, { "latitude": 55.701083, "longitude": 13.183756 })

@app.route('/planner', methods=['POST'])
def route_planner():
    Addresses =  json.loads(request.data.decode())
    FromAddress = Addresses['faddr']
    # ToAddress = Addresses['taddr']
    from_location = geolocator.geocode(FromAddress + region, timeout=None)
    # print(from_location)
    # to_location = geolocator.geocode(ToAddress + region, timeout=None)
    
    return planner({ "latitude": from_location.latitude, "longitude": from_location.longitude }, { "latitude": 55.701083, "longitude": 13.183756 })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5002')
