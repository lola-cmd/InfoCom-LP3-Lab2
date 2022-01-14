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

redis_server = redis.Redis(host="localhost", port="6379", decode_responses=True)

geolocator = Nominatim(user_agent="my_request")
region = ", Lund, Skåne, Sweden"

def find_avalaible_drone(drones):
    for key in drones:
        drone_info = json.loads(redis_server.get(key))
        drone_status = drone_info['status']
        if drone_status == 'idle':
            return key
    return None

def request_to_drone(key, coords):
    DRONE_URL = json.loads(redis_server.get(key))['url']
    DRONE_URL = 'http://' + DRONE_URL+':5000'
    with requests.session() as session:
        resp = session.post(DRONE_URL, json=coords)
        print(resp.text)

@app.route('/planner', methods=['POST'])
def route_planner():
    drones = redis_server.keys()
    Addresses =  json.loads(request.data.decode())
    FromAddress = Addresses['faddr']
    ToAddress = Addresses['taddr']
    from_location = geolocator.geocode(FromAddress + region, timeout=None)
    to_location = geolocator.geocode(ToAddress + region, timeout=None)
    if from_location is None:
        message = 'Departure address not found, please input a correct address'
        return message
    elif to_location is None:
        message = 'Destination address not found, please input a correct address'
        return message
    else:
        message = 'Get addresses!'
        coords = {'from': (from_location.longitude, from_location.latitude),
                  'to': (to_location.longitude, to_location.latitude),
                  }
        while len(drones) > 0:
            droneID = find_avalaible_drone(drones)
            if droneID is not None:
                try:
                    request_to_drone(droneID, coords)
                    return message
                except Exception as e:
                    print(e)
                    message = "Could not connect to the drone, try another drone"
                    drones.remove(droneID)
            else:
                message = 'no available drone, try later'
                return message

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5002')
