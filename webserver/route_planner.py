from flask import Flask, request, render_template, jsonify
from flask.globals import current_app 
from geopy.geocoders import Nominatim
from flask_cors import CORS
import redis
import json
import requests

app = Flask(__name__)
CORS(app, supports_credentials=True)
redis_server = redis.Redis(host="localhost", port="6379")

geolocator = Nominatim(user_agent="my_request")
region = ", Lund, Skåne, Sweden"
#================================================================
#Put the IP address of your drone
DRONE_URL = "http://DRONE_IP:5000"
#================================================================
@app.route('/planner', methods=['POST'])
def route_planner():
    Addresses =  json.loads(request.data.decode())
    FromAddress = Addresses['faddr']
    ToAddress = Addresses['taddr']
    
    current_location = (redis_server.get('longitude').decode(), redis_server.get('latitude').decode())
    from_location = geolocator.geocode(FromAddress + region)
    to_location = geolocator.geocode(ToAddress + region)
    if from_location is None:
        message = 'Departure address not found, please input a correct address'
        return message
    elif to_location is None:
        message = 'Destination address not found, please input a correct address'
        return message
    else:
        message = 'Get addresses! Send to Drone'
        coords = {'current': (current_location[0],current_location[1]),
                  'from': (from_location.longitude, from_location.latitude),
                  'to': (to_location.longitude, to_location.latitude),
                  }
        try:
            with requests.session() as session:
                resp = session.post(DRONE_URL, json=coords)
                print(resp.text)
            return message
        except Exception as e:
            print(e)
            return "Could not connect to the drone, please try again"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5002')
