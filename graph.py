from matplotlib import pyplot as plt

def plotPath(path):
    """
    Plots proposed path for visual feedback to the user
    
    :return Bool: Returns True or False depending if it was successful generating a figure.
    """

    try:
        x_values = []
        y_values = []
        for i in range(0, len(path)):
            x_values.append(path[i].getLongitude())
            y_values.append(path[i].getLatitude())
            plt.text(path[i].getLongitude(), path[i].getLatitude(), path[i].getName())

        plt.plot(x_values, y_values, 'b.', linestyle='solid')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.tight_layout(pad=2)
        plt.savefig('./static/images/tsp.jpg')
        plt.clf()

        return True
    except:
        return False

def plotTruePath(path, dronePath):
    """
    Plots proposed path overlayed with the drones flight path from previous flight.
    
    :return Bool: Returns True or False depending if it was successful generating a figure.
    """

    try:
        drone_x_values = []
        drone_y_values = []
        for i in range(0, len(dronePath)):
            drone_x_values.append(dronePath[i][1])
            drone_y_values.append(dronePath[i][0])
        
        x_values = []
        y_values = []
        for i in range(0, len(path)):
            x_values.append(path[i].getLongitude())
            y_values.append(path[i].getLatitude())
            plt.text(path[i].getLongitude(), path[i].getLatitude(), path[i].getName())

        plt.plot(x_values, y_values, label="Proposed Path", c="Blue", zorder=8)
        plt.plot(drone_x_values, drone_y_values, label="Flight Path", c="Red", zorder=9)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.tight_layout(pad=2)
        plt.legend()
        plt.savefig('./static/images/truepath.jpg')
        plt.clf()

        return True
    except:
        return False