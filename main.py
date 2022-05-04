from flask import Flask, render_template, request, redirect, url_for
import jyserver.Flask as jsf
import asyncio
import json
from coord import Coord
from travelling_salesman import calculateShortestPath
from graph import plotPath
from uav import UAV

destinations = []
obstacles = []
battery = 0

app = Flask(__name__)
uav = UAV()

@jsf.use(app)
class App:
    def __init__(self):
        self.is_connected = None
        self.battery = None
        self.flight_time = None
        self.route = []

        # asyncio.run(self.check_connection())
        # asyncio.run(self.get_battery())
        # asyncio.run(self.get_flight_time())

    async def check_connection(self):
        self.is_connected = await uav.connectToDrone()
    
    async def get_battery(self):
        self.battery = await uav.getBattery()
    
    async def get_flight_time(self):
        self.flight_time = await uav.getFlightTime()
        if self.flight_time != None:
            self.flight_time /= 60

    def calculatePath(self):
        d = []
        for x in destinations:
            d.append(Coord(x[1],float(x[2]),float(x[3])))

        p,cost = calculateShortestPath(d)

        r = []
        rNames = []
        for x in p:
            r.append(x)
            rNames.append(x.getName())
        
        self.route = r

        plotPath(p)
        
        self.js.document.getElementById('show-path-container').innerHTML = '<h2>Proposed Route: ' + str(rNames) + ', with a sum distance of ' + str(round(cost, 2)) + ' meters</h2><p class="label-light">* Order is from left to right</p><img src="/static/images/tsp.jpg"/>'

    def test(self):
        uav.start_flight(self.route)

@app.route('/load_json', methods=['GET'])
def load_json():
    with open('static/js/locations.json', 'r') as file:
        return json.load(file)

def save_json(data):
    with open('static/js/locations.json', 'w') as file:
        json.dump(data, file)

@app.route('/add_destination', methods=['POST'])
def add_destination():
    nickname = request.form['nickname']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    type = request.form['coordinate-type']
    from_history = request.form['from_history']

    if type == 'destination':
        uid = len(destinations)
        destinations.append([uid, nickname, latitude, longitude])
    elif type == 'obstacle':
        uid = len(obstacles)
        obstacles.append([uid, nickname, latitude, longitude])
    
    if from_history == 'no':
        history = load_json()
        jsonObj = {
            "name": nickname,
            "latitude": latitude,
            "longitude": longitude,
            "type": type,
            "id": len(history['locations'])
        }
        history['locations'].append(jsonObj)
        save_json(history)

    return redirect(url_for('index'))

@app.route('/remove_history_destination', methods=['POST'])
def remove_history_destination():

    id = int(request.form['id'])
    history = load_json()
    for i in range(0, len(history['locations'])):
        if history['locations'][i]['id'] == id:
            history['locations'].pop(i)
            break
    
    save_json(history)

    return 'ok'

@app.route('/remove_destination', methods=['POST'])
def remove_destination():
    n = int(request.form['id'])
    
    for x in destinations:
        if x[0] == n:
            destinations.pop(x[0])

    return redirect(url_for('index'))

@app.route('/remove_obstacle', methods=['POST'])
def remove_obstacle():
    n = int(request.form['id'])
    
    for x in obstacles:
        if x[0] == n:
            obstacles.pop(x[0])
    
    return redirect(url_for('index'))

@app.route('/refresh_status', methods=['POST'])
def refresh_status():
    asyncio.run(App.check_connection())
    asyncio.run(App.get_battery())
    asyncio.run(App.get_flight_time())

    return redirect(url_for('index'))

@app.route('/')
def index():
    history = load_json()
    return App.render(render_template('index.html', status=App.is_connected, battery=App.battery, flight_time=App.flight_time, destinations=destinations, obstacles=obstacles, history=history['locations']))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
