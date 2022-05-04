class Coord:

    def __init__(self, _name, _lat, _long):
        self.name = _name
        self.latitude = _lat
        self.longitude = _long
    
    def getName(self):
        return self.name
    
    def getLatitude(self):
        return self.latitude

    def getLongitude(self):
        return self.longitude