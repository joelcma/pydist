import sys
import itertools
import geopy.distance
from pyproj import Transformer

# Determine the root path of the project
root_path = "/".join(__file__.split("/")[:-1]) + "/"


def find_city_by_name(name, cities):
    if "/" in name:
        (name, country) = name.split("/")
        cities = find_city_by_country(country, cities)

    found = [city for city in cities if city.name.lower() == name.lower()]
    return found if found else None


def find_city_by_country(name, cities):
    found = [city for city in cities if city.country.lower() == name.lower()]
    return found if found else None


def distance_between_coordinates(lat1, lon1, lat2, lon2):
    return geopy.distance.geodesic((lat1, lon1), (lat2, lon2)).km


def validate_found_cities(city, cities):
    if cities is None:
        print(f"City {city} not found")
        sys.exit(1)

    if len(cities) > 1:
        print(f"Multiple cities found for {city}:")
        for c in cities:
            print(c)
        sys.exit(1)

    return cities[0]


def find_nearest_city(lat, lon, cities):
    return min(
        cities,
        key=lambda city: distance_between_coordinates(
            lat, lon, city.latitude, city.longitude
        ),
    )


class City:
    def __init__(self, line):
        (lineNumber, country, name, latitude, longitude, population) = (
            line.replace('"', "").replace("\n", "").split(";")
        )
        self.country = country
        self.name = name
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.population = population

    def __str__(self):
        return f"{self.name}, {self.country}"

    def distance(self, city):
        return distance_between_coordinates(
            self.latitude, self.longitude, city.latitude, city.longitude
        )


# Read CSV file
f = open(f"{root_path}cities.csv", "r")
cities = [City(line) for line in f.readlines()]
f.close()

args = sys.argv[1:]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def args_are_coordinates(args):
    return all(is_number(arg) for arg in args)


def args_are_cities(args):
    return all(isinstance(arg, str) for arg in args)


if args_are_coordinates(args):
    try:
        lat1, lon1, lat2, lon2 = map(float, args)
        distance = distance_between_coordinates(lat1, lon1, lat2, lon2)
        nearest_city1 = find_nearest_city(lat1, lon1, cities)
        nearest_city2 = find_nearest_city(lat2, lon2, cities)

        print(
            f"Distance between ({lat1}, {lon1}) and ({lat2}, {lon2}) is {distance:.2f} km"
        )
        print(f"Nearest city to ({lat1}, {lon1}) is {nearest_city1}")
        print(f"Nearest city to ({lat2}, {lon2}) is {nearest_city2}")
    except ValueError:
        print("Invalid coordinates. Expected four numbers.")
        sys.exit(1)

elif args_are_cities(args):
    city_objs = []
    for arg in args:
        found_cities = find_city_by_name(arg, cities)
        city_objs.append(validate_found_cities(arg, found_cities))

    for city1, city2 in itertools.combinations(city_objs, 2):
        print(
            f"The distance between {city1} and {city2} is: {city1.distance(city2)} km"
        )
else:
    print(
        "Usage: python script.py <city1> <city2> ... OR python script.py <lat1> <lon1> <lat2> <lon2>"
    )
    sys.exit(1)
