'''
Module that generates map with
10 films which were filmed close
to the given location
'''
import re
from math import asin, sin, pi, cos
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable

def extract_necessary_information(file: str) -> dict:
    '''
    Create new file, with only necessary information:
    films and location
    '''
    res = []
    film_list = []

    with open(file, "rb") as input_file:
        for line in input_file:
            try:
                line = line.decode("utf-8")
            except UnicodeDecodeError:
                continue

            if "{" in line:
                line = line[:line.index("{")] + line[line.index("}") + 1:]

            if "Federal" in line:
                continue

            res.append(line)

        res = list(set(res[14:-1]))

    for line in res:
        line = line.strip().split("\t")

        while "" in line:
            line.remove("")

        try:
            year = re.search(r"\(\d\d\d\d\)", line[0]).group(0)
        except AttributeError:
            continue

        line[1] = line[1].split(",")

        line[1] = ",".join(line[1][-3:])

        film_list.append([line[0], year, line[1]])

    return film_list

def get_list_by_year(films: list, year: int) -> list:
    '''
    Create a list based on a given year
    '''
    res = {}

    for film in films:
        if int(film[1][1:-1]) == year:
            film.remove(film[1])
            res[film[1]] = film[0]

    return res

def get_closest_locations(films: dict, location: tuple) -> list:
    '''
    Get closest locations of films to the given location
    '''
    geolocator = Nominatim(user_agent = "film_map")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds = 0.5)

    loc_dict = {}
    res = []

    for film in films:
        while len(res) < 11:
            try:
                loc_film = geolocator.geocode(film)

                film_location = (loc_film.latitude, loc_film.longitude)

                dist = distance_on_sphere(location, film_location)

                if dist < 1000000:
                    res.append((dist, films[film], film_location))

                loc_dict[dist] = films[film]

            except (AttributeError, GeocoderUnavailable, TypeError):
                pass
            break

    return res


def distance_on_sphere(location_1: tuple, location_2: tuple) -> float:
    '''
    Calculate distance between two locations
    '''
    earth_radius = 6371000
    lat_rad_1 = location_1[0] * (pi / 180)
    long_rad_1 = location_1[1] * (pi / 180)
    lat_rad_2 = location_2[0] * (pi / 180)
    long_rad_2 = location_2[1] * (pi / 180)

    first = sin((long_rad_2 - long_rad_1) / 2)**2
    second = cos(long_rad_1) * cos(long_rad_2) * sin((lat_rad_2 - lat_rad_1) / 2)**2

    dist = 2 * earth_radius * asin((first + second)**0.5)

    return dist

def map_generator(locations: list, start_location: tuple, year: int) -> None:
    '''
    Generates map with markers
    '''
    points = []

    gen_map = folium.Map(location=start_location)

    marker_layer = folium.FeatureGroup(name="Markers with fims")

    for loc in locations:
        folium.Marker(location=loc[2], popup=loc[1]).add_to(marker_layer)

    folium.Marker(location=start_location, popup="You are here!",
    icon = folium.Icon(color='green',icon='plus')).add_to(marker_layer)

    marker_layer.add_to(gen_map)

    for i in locations:
        points.append(i[2])

    lines = folium.FeatureGroup("Lines")

    for point in points:
        folium.PolyLine([point, start_location], color='red').add_to(lines)

    lines.add_to(gen_map)

    gen_map.add_child(folium.LayerControl())

    gen_map.save(str(year) + "_movies_map.html")

def main():
    '''
    Main function
    '''
    lat, longt = 49.83826, 24.02324
    year = 2000
    year = int(input("Please enter a year you would like to have a map for: "))
    lat, longt = tuple(map(float,
    input("Please enter your location (format: lat, long): ").split(", ")))

    print("Map is generating...\nPlease wait...")
    film_by_year = get_list_by_year(extract_necessary_information("locations.list"), 2000)

    closest_locations = get_closest_locations(film_by_year, (lat, longt))

    map_generator(closest_locations, (lat, longt), year)
    print(f"Finished. Please have look at the map {year}_movies_map.html")


if __name__ == "__main__":
    main()
