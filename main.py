import sys
import itertools
import geopy.distance

# Determine the root path of the project
root_path = "/".join(__file__.split("/")[:-1]) + "/"


def find_city_by_name(name, cities):
    name, country = name.split("/") if "/" in name else (name, None)
    cities = find_city_by_country(country, cities) if country else cities
    return [city for city in cities if city.name.lower() == name.lower()] or None


def find_city_by_country(name, cities):
    return [city for city in cities if city.country.lower() == name.lower()] or None


def distance_between_coordinates(lat1, lon1, lat2, lon2):
    return geopy.distance.geodesic((lat1, lon1), (lat2, lon2)).km


def validate_found_cities(city, cities):
    if not cities:
        sys.exit(f"City {city} not found")

    if len(cities) > 1:
        sys.exit(f"Multiple cities found for {city}:\n" + "\n".join(map(str, cities)))

    return cities[0]


def find_nearest_city(lat, lon, cities):
    return min(cities, key=lambda city: city.distance_to_coordinates(lat, lon))


class City:
    def __init__(self, line):
        data = line.replace('"', "").replace("\n", "").split(";")
        self.country, self.name, self.latitude, self.longitude, self.population = (
            data[1],
            data[2],
            float(data[3]),
            float(data[4]),
            data[5],
        )

    def __str__(self):
        return f"{self.name}, {self.country}"

    def distance(self, city):
        return distance_between_coordinates(
            self.latitude, self.longitude, city.latitude, city.longitude
        )

    def distance_to_coordinates(self, lat, lon):
        return distance_between_coordinates(self.latitude, self.longitude, lat, lon)


def load_cities(file_path):
    with open(file_path, "r") as f:
        return [City(line) for line in f.readlines()]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def args_are_coordinates(args):
    return len(args) == 4 and all(is_number(arg) for arg in args)


def args_are_cities(args):
    return args and all(isinstance(arg, str) for arg in args)


def main():
    args = sys.argv[1:]
    cities = load_cities(f"{root_path}cities.csv")

    if args_are_coordinates(args):
        lat1, lon1, lat2, lon2 = map(float, args)
        distance = distance_between_coordinates(lat1, lon1, lat2, lon2)
        nearest_city1 = find_nearest_city(lat1, lon1, cities)
        nearest_city2 = find_nearest_city(lat2, lon2, cities)

        print(
            f"Distance between ({lat1}, {lon1}) and ({lat2}, {lon2}) is {distance:.2f} km"
        )
        print(f"Nearest city to ({lat1}, {lon1}) is {nearest_city1}")
        print(f"Nearest city to ({lat2}, {lon2}) is {nearest_city2}")
    elif args_are_cities(args):
        city_objs = [
            validate_found_cities(arg, find_city_by_name(arg, cities)) for arg in args
        ]
        for city1, city2 in itertools.combinations(city_objs, 2):
            print(
                f"The distance between {city1} and {city2} is: {city1.distance(city2)} km"
            )
    else:
        sys.exit(
            "Usage: python script.py <city1> <city2> ... OR python script.py <lat1> <lon1> <lat2> <lon2>"
        )


if __name__ == "__main__":
    main()
