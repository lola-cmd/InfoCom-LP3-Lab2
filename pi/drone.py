from flask import Flask, request
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

@app.route('/', methods=['POST'])
def main():
    coords = request.json
    current_coord = coords['current']
    from_coord = coords['from']
    to_coord = coords['to']
    # CMD = ["python3", "simulator.py", '--cx', str(current_coord[0]), '--cy', str(current_coord[1]),
    #                                              '--px', str(pickup_coord[0]), '--py', str(pickup_coord[1]),
    #                                              '--dx', str(destination_coord[0]), '--dy', str(destination_coord[1])
    #       ]
    # print(CMD)
    subprocess.Popen(["python3", "simulator.py", '--clong', str(current_coord[0]), '--clat', str(current_coord[1]),
                                                 '--flong', str(from_coord[0]), '--flat', str(from_coord[1]),
                                                 '--tlong', str(to_coord[0]), '--tlat', str(to_coord[1])
                    ])
    return 'New route received'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
