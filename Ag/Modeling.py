from geopy.geocoders import Nominatim # Para OpenStreetMap
from geopy.exc import GeocoderTimedOut
from geopy.distance import geodesic
from Ag.Interface import Interface as ui
import requests
import googlemaps
import math

class PointOfInterest:
    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon

class Model:
    
    geolocator = Nominatim(user_agent="AG_routes")

    @staticmethod
    def name_to_coordinates(place_name): #geopy function -> API Nominatim (OpenStreetMap)
        # Realizar la geocodificación del nombre a coordenadas
        location = Model.geolocator.geocode(place_name)

        if location:
            latitude = location.latitude
            longitude = location.longitude
            ui.map_widget.set_position(latitude, longitude)
            return (latitude, longitude)
        else:
            return None

    @staticmethod
    def get_nearby_places(api_key, location, place_type, limit=10, radius=5000):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "key": api_key,
            "location": f"{location[0]},{location[1]}",
            "radius": radius,
            "type": place_type,
            "rankby": "prominence"
        }
        
        response = requests.get(url, params=params)
        results = response.json().get("results", [])
        
        places = []
        for place in results[:limit]:
            places.append(
                PointOfInterest(
                    place.get("name"),
                    place["geometry"]["location"]["lat"], #latitude
                    place["geometry"]["location"]["lng"], #longitude
                )
            )
        
        return places
    
    @staticmethod
    def harvesine_distance(coord1, coord2):
        R = 6371  # Radio de la Tierra en km

        lat1, lon1 = math.radians(coord1.lat), math.radians(coord1.lon)
        lat2, lon2 = math.radians(coord2.lat), math.radians(coord2.lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    @staticmethod
    def nearest_neighbor_path(route):
        unvisited = route[1:]
        path = [route[0]]
        last = path[-1]
        
        while unvisited:
            next_poi = min(unvisited, key=lambda poi: Model.harvesine_distance(last, poi))
            path.append(next_poi)
            unvisited.remove(next_poi)
        
        return path  # No regresamos al inicio
    
    @staticmethod
    def run_path(route):
        path = Model.nearest_neighbor_path(route)

        # Calcular y mostrar la distancia total
        total_distance = sum(Model.harvesine_distance(path[i], path[i+1]) for i in range(len(path)-1))
        total_duration = Model.estimate_travel_time(total_distance)
        return path, total_distance, total_duration

    @staticmethod
    def estimate_travel_time(distance, average_speed=50): #asumiendo una velocidad promedio
        return (distance / average_speed) * 60 #convertir a minutos