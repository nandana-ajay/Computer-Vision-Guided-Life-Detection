import numpy as np
from math import radians, cos, sin, asin, sqrt

def distance(lat1, lat2, lon1, lon2):
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result
    return c * r

def calculate_distance_matrix(geoloc):
    num_locations = len(geoloc)
    distance_matrix = np.zeros((num_locations, num_locations))

    for i in range(num_locations - 1):
        for j in range(i + 1, num_locations):
            lat1, lon1 = geoloc[i]
            lat2, lon2 = geoloc[j]
            dist = distance(lat1, lat2, lon1, lon2)
            distance_matrix[i][j] = dist
            distance_matrix[j][i] = dist

    return distance_matrix

def travellingsalesman(c):
    global cost, toPrint
    adj_vertex = 999
    min_val = 999
    visited[c] = 1
    print((c), end=" ")
    toPrint.append(c)  # Append the current node index to toPrint list
    for k in range(num_locations):
        if tsp_g[c][k] != 0 and visited[k] == 0:
            if tsp_g[c][k] < min_val:
                min_val = tsp_g[c][k]
                adj_vertex = k
    if min_val != 999:
        cost = cost + min_val
    if adj_vertex == 999:
        adj_vertex = 0
        print((adj_vertex), end=" ")
        toPrint.append(adj_vertex)  # Append the adjacent node index to toPrint list
        cost = cost + tsp_g[c][adj_vertex]
        return
    travellingsalesman(adj_vertex)

def calculate_shortest_path(geoloc):
    global num_locations, cost, visited, tsp_g, toPrint
    num_locations = len(geoloc)
    cost = 0
    visited = np.zeros(num_locations, dtype=int)
    toPrint = []  # Initialize the toPrint list
    tsp_g = calculate_distance_matrix(geoloc)

    print("Shortest Path:", end=" ")
    travellingsalesman(0)
    print()
    print("Minimum Cost:", end=" ")
    print(cost)
    print("Nodes visited in order:")
    for node in toPrint:
        print(node)
    return toPrint  # Return the toPrint list 

# Example usage
# geoloc = [[10.527642,76.214432],[10.107570,76.345665],[10.653460,76.232903],[11.3049669,75.7712146],[9.7130742,76.6831302]]
# calculate_shortest_path(geoloc)


