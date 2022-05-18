# Imports
from flask import Flask, render_template, request, redirect, url_for
import jyserver.Flask as jsf
import asyncio
import json
from coord import Coord
from travelling_salesman import calculateShortestPath
from graph import plotPath, plotTruePath
from uav import UAV

# Session variables
destinations = []
obstacles = []
battery = 0

# Initiate framework
app = Flask(__name__)

# Create UAV object
uav = UAV()

@jsf.use(app)
class App:
    def __init__(self):
        self.is_connected = None
        self.battery = None
        self.flight_time = None
        self.route = []
        self.drone_position = None

        asyncio.run(self.check_connection())
        self.get_battery()
        self.get_drone_pos(uav.gps_accuracy)

    async def check_connection(self):
        self.is_connected = await uav.connectToDrone()

    def get_battery(self):
        self.battery = uav.getBattery()

    def get_drone_pos(self, n):
        self.drone_position = uav.get_current_position(n)

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

    def get_past_log(self):
        log = None
        with open('static/js/flight_log.json', 'r') as file:
            log = json.load(file)

        plotTruePath(self.route, log['flight_log'])

        self.js.document.getElementById('show-drone-path-container').innerHTML = ''\
                    '<h2>Route of UAV from previous flight</h2><br/>'\
                        '<div class="flight-log">'\
                            '<div class="drone-path-graph">'\
                                '<img src="/static/images/truepath.jpg" width="100%"/>'\
                            '</div>'\
                            '<div class="drone-path-info">'\
                                '<div class="status-info coordinate-status">'\
                                    '<p class="status-text label-bold">'\
                                        'Start Battery:'\
                                        '<span class="gps-text"> ' + str(log['start_battery']) + '%</span>'\
                                    '</p>'\
                                '</div>'\
                                '<div class="status-info coordinate-status">'\
                                    '<p class="status-text label-bold">'\
                                        'End Battery:'\
                                        '<span class="gps-text"> ' + str(log['end_battery']) + '%</span>'\
                                    '</p>'\
                                '</div>'\
                            '</div>'\
                        '</div>'\

    
    def start(self):
        """
        Starts Flight
        """
        uav.start_flight(self.route)



@app.route('/load_json', methods=['GET'])
def load_json():
    """
    Reads json file that contains history of previously entered destinations

    :return Json: Returns json object of destinations
    """
    with open('static/js/locations.json', 'r') as file:
        return json.load(file)



def save_json(data):
    """
    Updates json file that contains history of previously entered destinations

    :param data: Json object to be saved to file
    """
    with open('static/js/locations.json', 'w') as file:
        json.dump(data, file)



@app.route('/add_destination', methods=['POST'])
def add_destination():
    """
    Adds destination to session variable and saves newly input destination into history
    """
    nickname = request.form['nickname']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    type = 'destination'
    from_history = request.form['from_history']

    if type == 'destination':
        uid = len(destinations)
        destinations.append([uid, nickname, latitude, longitude])
    # elif type == 'obstacle':
    #     uid = len(obstacles)
    #     obstacles.append([uid, nickname, latitude, longitude])
    
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

    """
    Removes stored destination from history

    :return string: Returns ok when complete
    """

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
    """
    Removes destination from session
    """

    n = int(request.form['id'])
    
    if n <= 1:
        destinations = []
    else:
        for x in destinations:
            if x[0] == n:
                destinations.pop(x[0])

    return redirect(url_for('index'))



@app.route('/remove_obstacle', methods=['POST'])
def remove_obstacle():
    """
    Removes obstacle from session
    """

    n = int(request.form['id'])
    
    if n <= 1:
        obstacles = []
    else:
        for x in obstacles:
            if x[0] == n:
                obstacles.pop(x[0])
    
    return redirect(url_for('index'))



@app.route('/refresh_status', methods=['POST'])
def refresh_status():
    """
    Reattempts to conect to drone and retrieve battery status.
    Then attempts to get current drone coordinates
    """

    asyncio.run(App.check_connection())
    App.get_battery()
    App.get_drone_pos(uav.gps_accuracy)

    return redirect(url_for('index'))



@app.route('/')
def index():
    """
    Renders Flask template through Jyserver
    """
    history = load_json()
    return App.render(render_template('index.html', status=App.is_connected, battery=App.battery, flight_time=App.flight_time, destinations=destinations, obstacles=obstacles, current_pos=App.drone_position, history=history['locations']))



if __name__ == '__main__':
    app.run(host='192.168.50.1', port=5000)
