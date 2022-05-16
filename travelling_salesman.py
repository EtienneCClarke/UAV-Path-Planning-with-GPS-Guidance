from collections import OrderedDict
from geographiclib.geodesic import Geodesic
import math
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

                # Calculate distance
                neighbours[str(j.getName())] = str(Geodesic.WGS84.Inverse(i.getLatitude(), i.getLongitude(), j.getLatitude(), j.getLongitude())['s12'])

        graph[i.getName()] = neighbours

    return graph

# def vincenty(latA, longA, latB, longB):

#     a,b = (6378137.0, 6356752.314245)
#     f = 298.257223563
#     L = longB - longA
#     TU1,TU2 = (f * math.tan(latA), f * math.tan(latB))
#     CU1,CU2 = (1 / math.sqrt((1 + TU1 * TU1)), 1 / math.sqrt((1 + TU2 * TU2)))
#     SU1,SU2 = (TU1 * CU1, TU2 * CU2)

#     lamda = L; sinLamda = None; cosLamda = None
#     sigma = None; sinSigma = None; cosSigma = None
#     cos2sigmaM = None
#     cosSqrAlpha = None

#     lamdaB = None

#     while True:
#         sinLamda = math.sin(lamda)
#         cosLamda = math.cos(lamda)
#         sinSqrAlpha = (CU2 * sinLamda) * (CU2 * sinLamda) + (CU1 * SU2 - SU1 * CU2 * cosLamda)
#         sinSigma = math.sqrt(sinSqrAlpha)
#         cosSigma = SU1 * SU2 + CU1 * CU2 * cosLamda
#         sigma = math.atan2(sinSigma * cosSigma)
#         sinAlpha = CU1 * CU2 * sinLamda / sinSigma
#         cosSqrAlpha = 1 - sinAlpha * sinAlpha
#         cos2sigmaM = cosSigma - 2 * SU1 * SU2 / cosSqrAlpha
#         C = f / 16 * cosSqrAlpha * (4 + f * (4-3*cosSqrAlpha))
#         lamdaB = lamda
#         lamda = L + (1 - C) * f * sinAlpha * (sigma + C * sinSigma * (cos2sigmaM + C * cosSigma * (-1 + 2 * cos2sigmaM * cos2sigmaM)))

#         if lamdaB - lamda > 1e-12:
#             break
    
#     uSqr = cosSqrAlpha * (a * a - b * b) / (b * b)
#     A = 1 + uSqr/16384 * (4096 + uSqr * (-768 + uSqr * (320 - 175 * uSqr)))
#     B = uSqr / 1024 * (256 + uSqr * (-128 + uSqr * (74-47 * uSqr)))
#     deltaSigma = B * sinSigma * (cos2sigmaM + B / 4 * (cosSigma * (-1 + 2 * cos2sigmaM * cos2sigmaM) - B / 6 * cos2sigmaM * (-3 + 4 * sinSigma * sinSigma) * (-3 + 4 * cos2sigmaM * cos2sigmaM)))

         

def nearestNeighbour(g):

    # final route output
    route = []
    route_cost = 0
    graph = list(g.items())
    n = len(graph)
    current_node = graph[0]
    route.append(str(current_node[0]))

    for i in range(0, n):

        neighbours = graph[graph.index(current_node)][1]

        nearest_neighbour = ""
        nearest_neighbour_cost = float('inf')
        for node in neighbours:

            neighbour = str(node[0])
            cost = float(neighbours[node])

            if neighbour not in route:
                if cost < nearest_neighbour_cost:
                    nearest_neighbour_cost = cost
                    nearest_neighbour = neighbour

        for node in graph:
            if str(node[0]) == nearest_neighbour:
                current_node = node
        
        if nearest_neighbour_cost < float('inf'):
            route_cost += nearest_neighbour_cost

        route.append(nearest_neighbour)

    route.pop()

    return (route, route_cost)


def calculateShortestPath(destinations):

    nn,cost = nearestNeighbour(generateGraph(destinations))
    path = []

    for x in nn:
        for y in destinations:
            if x == y.getName():
                path.append(y)

    return (path,cost)
