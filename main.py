#this is gonna be some seriously fucked up code i fear
#idk if the python csv module will even be able to handle the sheer mass of a gtfs text file
    #update to my surprise it seems that it can
import csv
from geopy.distance import geodesic as gd

class Gshape:
    def __init__(self, agency, id):
        self.__points = []

        shapes_file = open("./" + agency + "/shapes.txt", "r", newline="")
        reader = csv.reader(shapes_file)

        for i in reader:
            if(i[0] == id):
                self.__points.append(i)
        
        self.__total_len = float(self.__points[len(self.__points)-1][4])

        shapes_file.close()
        
    def get_len(self):
        return self.__total_len

    def __find_nearest_point(self, coords):
        best_point = 0
        best_dist = gd((self.__points[0][1], self.__points[0][2]), coords)
        for i in range(1, len(self.__points) - 1):
            pt_coords = (float(self.__points[i][1]), float(self.__points[i][2]))
            if gd(pt_coords, coords) < best_dist:
                best_point = i
                best_dist = gd(pt_coords, coords)
        return best_point

    def get_shape_dist(self, coords1, coords2):
        ndx_one = self.__find_nearest_point(coords1)
        ndx_two = self.__find_nearest_point(coords2)
        dist = abs(float(self.__points[ndx_two][4]) - float(self.__points[ndx_one][4]))
        return dist


class Stop:
    def __init__(self, agency, id):
        self.__id = id

        stops_file = open("./" + agency + "/stops.txt", "r", newline="")
        reader = csv.reader(stops_file)

        next(reader)

        for i in reader:
            if i[0] ==self.__id:
                self.__name = i[2]
                self.__lat = i[4]
                self.__lon = i[5]

        stops_file.close()

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_coords(self):
        return (self.__lat, self.__lon)

class Trip:
    def __init__(self, agency, id):
        self.__stops = []

        stop_times_file = open("./" + agency + "/stop_times.txt", "r", newline="")
        reader = csv.reader(stop_times_file)

        next(reader)

        for i in reader:
            if(i[0] == id):
                self.__stops.append(Stop(agency, i[3]))
        
        stop_times_file.close()

    def get_first_stop(self):
        return self.__stops[0]

    def get_last_stop(self):
        return self.__stops[len(self.__stops) - 1]

    def get_nth_stop(self, n):
        return self.__stops[n]

    def get_stop_count(self):
        return len(self.__stops)
    
    def print_stops_list(self):
        for i in range(len(self.__stops)):
            print(i+1, ":", self.__stops[i].get_name())

#    def print_stops_list(self, start_ndx):
#        j = 0
#        for i in range(start_ndx, len(self.__stops)):
#            print(j, ":", self.__stops[i].get_name())

def main():
    print("Peyton's horridly clunky transit distance calculator. Version 0.1")
    agency = input("Enter an agency code: ")

    agency_file = open("./" + agency +"/agency.txt", "r", newline="")
    reader = csv.reader(agency_file)

    next(reader)

    for line in reader:
        print("Currently using GTFS data from:", line[1])

    agency_file.close()

    input("To continue, press enter")

    routes_file = open("./" + agency + "/routes.txt", "r", newline="")
    reader = csv.reader(routes_file)

    next(reader)

    routes = []

    print("The routes available in the feed are:")
    i = 1

    for line in reader:
        routes.append(line)
        print(i, ":", line[0], line[3])
        i += 1

    route_choice = routes[int(input("Please choose a route by entering the number indicated in its row: ")) - 1]

    print("You have chosen: ", route_choice[0], route_choice[3])
    input("Press enter to continue")

    routes_file.close()

    directions_file = open("./" + agency + "/directions.txt", "r", newline="")
    reader = csv.reader(directions_file)

    next(reader)

    directions = []

    print("The directions available for this route are:")
    i = 1

    for line in reader:
        if line[0] == route_choice[0]:
            directions.append(line)
            print(i, ":", line[3], "–", line[2])
            i += 1

    direction_choice = directions[int(input("Please choose a direction by entering the number indicated in its row: ")) - 1]

    print("You have chosen: ", direction_choice[3])
    input("Press enter to continue")
    print("Finding variations – This may take a while")

    directions_file.close()

    trips_file = open("./" + agency + "/trips.txt", "r", newline="")
    reader = csv.reader(trips_file)

    header = next(reader)
    direction_id_ndx = header.index("direction_id")
    shape_id_ndx = header.index("shape_id")
    trip_id_ndx = header.index("trip_id")
    trip_headsign_ndx = header.index("trip_headsign")

    possible_trips = []
    possible_shape_ids = []
    possible_shapes = []
    possible_names = []

    for line in reader:
            if(line[0] == route_choice[0] and line[direction_id_ndx] == direction_choice[1] and possible_shape_ids.count(line[shape_id_ndx]) == 0):
                possible_trips.append(Trip(agency, line[trip_id_ndx]))
                possible_shape_ids.append(line[shape_id_ndx])
                possible_shapes.append(Gshape(agency, line[shape_id_ndx]))
                possible_names.append(line[trip_headsign_ndx])
    
    print("The following variations have been found:")
    for i in range(len(possible_trips)):
        print(i+1, ":", possible_names[i], "of length", possible_shapes[i].get_len(), "with initial stop", possible_trips[i].get_first_stop().get_name(), "and last stop", possible_trips[i].get_last_stop().get_name(), "and", possible_trips[i].get_stop_count(), "total stops")

    variant_choice = int(input("Please choose a variation by entering the number indicated in its row: ")) - 1

    trips_file.close()

    trip = possible_trips[variant_choice]
    shape = possible_shapes[variant_choice]

    print("The stops on the trip you have selected are:")
    trip.print_stops_list()

    starting_stop = trip.get_nth_stop(int(input("Please enter the number corresponding to your starting stop: ")) - 1)
    ending_stop = trip.get_nth_stop(int(input("Please enter the number corresponding to your ending stop: ")) - 1)

    starting_coords = starting_stop.get_coords()
    ending_coords = ending_stop.get_coords()

    result = shape.get_shape_dist(starting_coords, ending_coords)

    result_miles = result * 0.6213712

    print ("The distance between the selected stops is:", round(result, 2), "kilometers (", round(result_miles, 2), "miles)")
    

main()