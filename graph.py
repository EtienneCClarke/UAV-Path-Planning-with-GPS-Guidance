from matplotlib import pyplot as plt

def plotPath(path):

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
        plt.close()

        return True
    except:
        return False