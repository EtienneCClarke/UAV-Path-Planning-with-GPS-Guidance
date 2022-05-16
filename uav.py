from pa1010d import PA1010D
from djitellopy import Tello
from geographiclib.geodesic import Geodesic
import json
import time

drone = Tello('192.168.50.138')
gps = PA1010D()

class UAV:

    def __init__(self):
        self.flying = False
        self.current_heading = 0 # 0 = North, 90 = East, 180 = South, 270 = West
        self.gps_accuracy = 15
        self.flight_log = {
            "start_battery" : 0,
            "end_battery" : 0,
            "flight_log": []
        }

    async def connectToDrone(self):
        """
        Creates connection with tello drone

        :return Bool: Returns True if successful, False if not
        """
        try:
            drone.connect()
            return True
        except:
            return False

    def getBattery(self):
        """
        Retrieves current battery level

        :return Int: Returns battery level as integer, Returns None if no connection
        """
        try:
            return drone.get_battery()
        except:
            return None

    async def getFlightTime(self):
        """
        Retrieves flight time of drone in current session

        :return float: Returns time the motors have been active in seconds, Returns None if no connection
        """
        try:
            return drone.get_flight_time()
        except:
            return None

    def emergencyStop(self):
        """
        In emergency stop drone and attempt to land- If unable to do so stop rotors
        """
        try:
            drone.send_control_command('stop')
            drone.land()
        except:
            drone.emergency()
    
    def save_log(self, data):
        with open('static/js/flight_log.json', 'w') as file:
            json.dump(data, file)

    def update_log(self, lat, long):
        self.flight_log['flight_log'].append([lat, long])
        self.flight_log['end_battery'] = self.getBattery()
        self.save_log(self.flight_log)


    # Begins flight
    def start_flight(self, route):

        self.flight_log['start_battery'] = self.getBattery()

        try:
            self.initial_calibration()
        except:
            print('could not calibrate')

        time.sleep(3)
        # Attempt to takeoff
        try:
           drone.takeoff()
        except:
           print('error')
        
        #Fly to each location
        visited = []
        for i in route:
            if i.getName() not in visited:
               try:
                   self.fly_to(i.getLatitude(), i.getLongitude())
                   visited.append(i.getName())
               except:
                   print('Could not navigate to destination')
                   drone.land()

        # Attempt to land
        try:
            drone.land()
        except:
            print('error')

    def initial_calibration(self):
        """
        Calibrates where the drone is facing. Takes average gps recording of two positions
        then calculates the heading.

        :return Bool: Returns True when calibration is complete
        """
        start_lat, start_long = self.get_current_position(self.gps_accuracy)

        try:
            drone.takeoff()
        except:
            print('error taking off')

        drone.send_control_command('forward 500')
        drone.send_control_command('forward 500')

        try:
            drone.land()
        except:
            print('Error landing')

        end_lat, end_long = self.get_current_position(self.gps_accuracy)

        self.current_heading = self.get_edge_data(start_lat, start_long, end_lat, end_long)['azi1']
        if self.current_heading < 0:
            self.current_heading = round(360 + self.current_heading)

        return True

    def fly_to(self, lat, long):
        """
        Fly towards a set of coordinates

        :param lat: Latitude value of destination
        :param long: Longitude value of destination
        :return Bool: Returns True if it has reached its destination
        """
        while True:

            # Is there enough battery
            if self.getBattery() <= 30:
                return False

            # Get current GPS coordinates
            current_lat, current_long = self.get_current_position(self.gps_accuracy)
            # current_lat, current_long = (53.48507523811314, -2.2496590652130206)

            # Check if drone is at desired coordinates
            if current_lat < lat + 0.00002 and current_lat > lat - 0.00002:
                if current_long < long + 0.00002 and current_long > long - 0.00002:
                    return True

            # lat, long = (53.48542391616002, -2.2506294124744874)

            # Get Edge Data
            edge_data = self.get_edge_data(current_lat, current_long, lat, long)

            # Calculate angle, direction to turn, and distance to destination
            a, cw = self.calc_rotation(edge_data)
            distance = round(edge_data['s12'] * 100) # convert to  cm

            self.update_log(current_lat, current_long)

            # rotate to face destination if greater than 
            if a != 0:
                if cw:
                    # drone.send_control_command('cw ' + str(a))
                    sum_a = self.current_heading + a
                    if sum_a == 360:
                        self.current_heading = 0
                    elif sum_a < 360:
                        self.current_heading = sum_a
                    else:
                        self.current_heading = sum_a - 360

                else:
                    # drone.send_control_command('ccw ' + str(a))
                    sum_a = self.current_heading - a
                    if sum_a >= 0:
                        self.current_heading = sum_a
                    else:
                        self.current_heading = sum_a + 360

            # Move to destination if less than or equal to 5 meters, else move forward 5 meters 
            if distance <= 500:
                drone.send_control_command('forward ' + str(distance))
            else:
                drone.send_control_command('forward 500')



    def get_edge_data(self, latA, longA, latB, longB):
        """
        Calculates data between two coordinates, e.g. azimuths, distance

        :param latA: Latitude value of the first coordinate
        :param longA: Longitude value of the first coordinate
        :param latB: Latitude value of the second coordinate
        :param longB: Longitude value of the second coordinate
        :return Dictionary: Data containing both coordinates, their distance apart, relative azimuths, and spherical arc length
        """
        return Geodesic.WGS84.Inverse(latA, longA, latB, longB)



    def get_current_position(self, n):
        """
        Calculates an approximate gps coordinate of the drones location

        :param n: Number of coordinates to take before calculating an average
        :return (Float, Float): Latitude and Longitude as a tuple
        """
        latitude = 0
        longitude = 0
        count = 0
        while count < n:
            result = gps.update()
            if result and gps.latitude is not None:
                latitude += gps.latitude
                longitude += gps.longitude
                count += 1
            else:
                return (0, 0)

        return(latitude / n, longitude / n)



    def calc_rotation(self, data):
        """
        Calculates the angle and shortest rotational direction needed to face towards a coordinate

        :param data: Dictionary of data produced by the get_edge_data function
        :return (Int, Bool): Angle to turn and Boolean confirms if turning clockwise is quicker than counter clockwise- returned as tuple
        """
        # bearing in degrees to next point from north, 0 to 180 = eastwards, 0 to -180 = westwards
        bearing = round(data['azi1'])

        # Convert to bearing in degrees from north between 0 and 360
        if bearing < 0:
            bearing = 360 + bearing

        # Returns angle and direction to turn, clockwise = True | counter clockwise = False, 
        if self.current_heading != bearing:
            if self.current_heading <= 180:
                if bearing > self.current_heading and bearing < self.current_heading + 180:
                    a = bearing - self.current_heading
                    return (a, True)
                else:
                    if bearing > 0 and bearing < self.current_heading:
                        a = self.current_heading - bearing
                        return (a, False)
                    else:
                        a = (360 - bearing) + self.current_heading
                        return (a, False)
            else:
                if bearing < self.current_heading and bearing > self.current_heading - 180:
                    a = self.current_heading - bearing
                    return (a, False)
                else:
                    if bearing > 0 and bearing < self.current_heading - 180:
                        a = (360 - self.current_heading) + bearing
                        return(a, True)
                    else:
                        a = bearing - self.current_heading
                        return(a, True)

        # Return 0 if facing correct direction
        return (0, True)