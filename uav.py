from pa1010d import PA1010D
from djitellopy import Tello
from geographiclib.geodesic import Geodesic
from coord import Coord
import time

drone = Tello('192.168.50.138')
gps = PA1010D()

class UAV:

    def __init__(self):
        self.flying = False
        self.current_heading = 0 # 0 = North, 90 = East, 180 = South, 270 = West
        self.flight_log = []

    async def connectToDrone(self):
        try:
            drone.connect()
            return True
        except:
            return False

    async def getBattery(self):
        try:
            return drone.get_battery()
        except:
            return None

    async def getFlightTime(self):
        try:
            return drone.get_flight_time()
        except:
            return None
    
    async def emergencyStop(self):
        try:
            drone.land()
        except:
            drone.emergency()

    # Begins flight
    def start_flight(self, route):

        try:
            self.initial_calibration((route[0].getLatitude(),route[0].getLongitude()))
        except:
            print('Error Calibrating')

        # Attempt to takeoff
        try:
            drone.takeoff()
        except:
            print('error')
        
        # Fly to each location
        for i in route:
            print(i.getName(), i.getLatitude(), i.getLongitude())
            # self.fly_to(i.getLatitude(), i.getLongitude())

        # Attempt to land
        try:
            drone.land()
        except:
            print('error')

    def initial_calibration(self, route_start):
        
        try:
            drone.takeoff()
        except:
            print('error taking off')
            return False

        start_lat, start_long = self.get_current_position(5)

        drone.send_control_command('forward 150')

        end_lat, end_long = self.get_current_position(5)

        self.current_heading = self.get_edge_data(start_lat, start_long, end_lat, end_long)['azi1']

        self.fly_to(route_start[0], route_start[1])

        drone.land()

        return True

    def get_current_position(self, max_iterations):
        # store current GPS coordinates 5 times, 2 per second
        latitude = 0
        longitude = 0
        for i in range(0, max_iterations):
            time.sleep(0.5)
            gps.update()
            latitude += gps.latitude
            longitude += gps.longitude
        
        return (latitude / max_iterations, longitude / max_iterations)

    def fly_to(self, lat, long):

        # Loop until reached detination
        while True:

            # Get current GPS coordinates
            gps.update()

            # Log current location
            self.log.append((gps.latitude, gps.longitude))

            #Check if destination has been reached
            if gps.longitude < long + 0.0000025 and gps.longitude > long - 0.0000025:
                if gps.latitude < lat + 0.0000025 and gps.latitude > lat - 0.0000025:
                    return True

            edge_data = self.get_edge_data(gps.latitude, gps.longitude, lat, long)
                
            a, cw = self.calc_rotation(edge_data)
            distance = edge_data['s12'] * 100 # convert to cm

            # rotate to face destination
            if a > self.current_heading + 2 and a < self.current_heading - 2:
                if cw:
                    drone.send_control_command('cw ' + str(a))
                else:
                    drone.send_control_command('ccw ' + str(a))

            # Move to destination if less than 4.5 meters, else move forward 4.5 meters 
            if distance < 450:
                drone.send_control_command('forward ' + str(distance))
            else:
                drone.send_control_command('forward 450')
    
    # Returns data between two points, e.g. distance, bearing etc...
    def get_edge_data(self, latA, longA, latB, longB):
        return Geodesic.WGS84.Inverse(latA, longA, latB, longB)

    def calc_rotation(self, edge):

        # bearing in degrees to next point from north, 0 to 180 = eastwards, 0 to -180 = westwards
        bearing = round(edge['azi1']) # Must be Int to work with tello SDK
        
        # Convert to bearing in degrees from north between 0 and 360
        if bearing < 0:
            bearing = 360 + bearing

        # Returns angle and direction to turn, clockwise = True | anti-clickwise = False, 
        if self.current_heading != bearing:
            if self.current_heading < 180:
                if bearing < self.current_heading + 180 and bearing > self.current_heading:
                    return (bearing - self.current_heading, True)
                else:
                    if bearing > 0 and bearing < self.current_heading:
                        return (self.current_heading - bearing, False)
                    else:
                        return (360 - bearing + self.current_heading, False)
            else:
                if bearing < self.current_heading and bearing > self.current_heading - 180:
                    return (self.current_heading - bearing, False)
                else:
                    if bearing > self.current_heading:
                        return(bearing - self.current_heading, True)

        # Return 0 if facing correct direction
        return (0, True)