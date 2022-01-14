from flask import Flask, request
from flask_cors import CORS
import subprocess
import  requests


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'


myID = "Drone1"
print(myID)
init_location = (13.21008, 55.71106)
try:
    with open('drone_location.txt', 'r') as file:
        current_location = file.read()
        current_longitude = float(current_location.split(',')[0])
        current_latitude = float(current_location.split(',')[1])
except FileNotFoundError:
    current_longitude = init_location[0]
    current_latitude = init_location[1]
    with open('drone_location.txt', 'w+') as file:
        file.write(str(current_longitude) + ',' + str(current_latitude))

drone_info = {'id': myID,
                'longitude': current_longitude,
                'latitude': current_latitude,
                'status': 'idle'}
print(drone_info)

DATABASE="http://192.168.1.35:5001/drone"
with requests.Session() as session:
    resp = session.post(DATABASE, json=drone_info)
print('done')

@app.route('/', methods=['POST'])
def main():
    coords = request.json
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
    app.run(debug=True, host='0.0.0.0')
