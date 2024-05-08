from flask import Flask, request
from flask_cors import CORS
import redis
import json


app = Flask(__name__)
CORS(app)

# change this to connect to your redis server
# ===============================================
redis_server = redis.Redis(host="localhost", port=6379, decode_responses=True, charset="unicode_escape")
# ===============================================

@app.route('/drone', methods=['POST'])
def drone():
    drone = request.get_json()
    droneIP = request.remote_addr
    droneID = drone['id']
    drone_longitude = drone['longitude']
    drone_latitude = drone['latitude']
    drone_status = drone['status']
    # Get the infomation of the drone in the request, and update the information in Redis database
    # Data that need to be stored in the database: 
    # Drone ID, logitude of the drone, latitude of the drone, drone's IP address, the status of the drone
    # Note that you need to store the mentioned infomation for all drones in Redis, think carefully how to store them
    # =========================================================================================

    
    redis_server.set(droneID, json.dumps({
        "ip": droneIP,
        "long": drone_longitude,
        "lat": drone_latitude,
        "status": drone_status
    }))


     # =======================================================================================
    return 'Get data'

if __name__ == "__main__":


    app.run(debug=True, host='127.0.0.1', port='5001')
