from flask import Flask, request
from flask_cors import CORS
import subprocess
import  requests

from pi.simulator import SERVER_URL

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

@app.route('/', methods=['POST'])
def main():
    coords = request.json
    myID = app.config.get('id')
    with open('drone_location.txt', 'r') as file:
        current_location = file.read()
        current_longitude = float(current_location.split(',')[0])
        current_latitude = float(current_location.split(',')[0])
    from_coord = coords['from']
    to_coord = coords['to']
    subprocess.Popen(["python3", "simulator.py", '--clong', str(current_longitude), '--clat', str(current_latitude),
                                                 '--flong', str(from_coord[0]), '--flat', str(from_coord[1]),
                                                 '--tlong', str(to_coord[0]), '--tlat', str(to_coord[1]),
                                                 '--id', myID
                    ])
    return 'New route received'

if __name__ == '__main__':
    myID = "Drone1"
    init_location = (13.21008, 55.71106)
    try:
        with open('drone_location.txt', 'r') as file:
            current_location = file.read()
            current_longitude = float(current_location.split(',')[0])
            current_latitude = float(current_location.split(',')[0])
    except FileNotFoundError:
        current_longitude = init_location[0]
        current_latitude = init_location[1]
        with open('drone_location.txt', 'w+') as file:
            file.write(str(current_longitude) + ',' + str(current_latitude))

    drone_info = {'id': myID,
                  'longitude': current_longitude,
                  'latitude': current_latitude,
                  'status': 'idle'}
    DATABASE="http://WEBSERVER_IP:5001/drone"
    with requests.Session() as session:
        resp = session.post(DATABASE, json=drone_info)
    app.config['id'] = myID
    app.run(debug=True, host='0.0.0.0')
