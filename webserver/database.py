from flask import Flask, request
from flask_cors import CORS
import redis
import json


app = Flask(__name__)
CORS(app, supports_credentials=True)
# app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

# change this to connect to your redis server
# ===============================================
redis_server = redis.Redis("localhost", decode_responses=True, charset="unicode_escape")
# ===============================================

@app.route('/drone', methods=['POST'])
def drone():
    drone = request.get_json()
    droneURL = request.url
    drone_info = {'longitude': drone['longitude'],
                  'latitude': drone['latitude'],
                  'url': droneURL,
                  'status': drone['status']}
    print(drone_info)
    redis_server.set(drone['id'], json.dumps(drone_info))
    return 'Get data'

if __name__ == "__main__":


    app.run(debug=True, host='0.0.0.0', port='5001')
