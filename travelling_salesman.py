from collections import OrderedDict
from geographiclib.geodesic import Geodesic
from coord import Coord

def generateGraph(destinations):
    
    # using ordered dictionary over regular dictionary is important for the nearest neighbour implementation
    graph = OrderedDict()

    # loop through each destination
    for i in destinations:

        # create an empty list of neighbours
        neighbours = {}

        # loop through all other destinations
        for j in destinations:
            if i != j:

                # Create coordinate tuples
                coordinate_A = (i.getLongitude(), i.getLatitude())
                coordinate_B = (j.getLongitude(), j.getLatitude())

                print(Geodesic.WGS84.Inverse(i.getLatitude(), i.getLongitude(), j.getLatitude(), j.getLongitude()))
                # Calculate distance
                neighbours[j.getName()] = str(Geodesic.WGS84.Inverse(i.getLatitude(), i.getLongitude(), j.getLatitude(), j.getLongitude())['s12'])

        graph[i.getName()] = neighbours

    return graph

def nearestNeighbour(g):

    # final path output
    path = []
    path_cost = 0
    graph = list(g.items())
    n = len(graph)
    current_node = graph[0]
    path.append(current_node[0])

    for i in range(0, n):

        neighbours = graph[graph.index(current_node)][1]

        nearest_neighbour = ''
        nearest_neighbour_cost = float('inf')
        for node in neighbours:

            neighbour = node[0]
            cost = float(neighbours[node])

            if neighbour not in path:
                if cost < nearest_neighbour_cost:
                    nearest_neighbour_cost = cost
                    nearest_neighbour = neighbour

        for node in graph:
            if node[0] == nearest_neighbour:
                current_node = node
        
        if nearest_neighbour_cost < float('inf'):
            path_cost += nearest_neighbour_cost

        path.append(nearest_neighbour)

    path.pop()

    return (path, path_cost)


def calculateShortestPath(destinations):

    nn,cost = nearestNeighbour(generateGraph(destinations))
    path = []

    for x in nn:
        for y in destinations:
            if x == y.getName():
                path.append(y)

    return (path,cost)
