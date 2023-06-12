from geopy.distance import geodesic as GD
from haversine import haversine, Unit
import sys

def get_meter_lat_lng(target: tuple, nowLocation: tuple):
    '''
    Usage: get_meter_lat_lng((lat1, lng1), (lat2, lng2))
    '''
    distance = GD(target, nowLocation).m
    return distance

def get_meter_haversine(target: tuple, nowLocation: tuple):
    '''
    Usage: get_meter_haversine((lat1, lng1), (lat2, lng2))
    '''
    distance = haversine(target, nowLocation, unit=Unit.METERS)
    return distance


if __name__ == "__main__":
    lng1 = float(sys.argv[1])
    lat1 = float(sys.argv[2])
    lng2 = float(sys.argv[3])
    lat2 = float(sys.argv[4])
    location1 = (lat1, lng1)
    location2 = (lat2, lng2)
    print(get_meter_haversine(location1, location2))