class Coord:
    """
    Coordinate object to store data about a GPS position

    :method getName: Returns name of coordinate object.\n
    :method getLatitude: Returns latitude of coordinate.\n
    :method getLongitude: Returns longitude of coordinate.\n
    """

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