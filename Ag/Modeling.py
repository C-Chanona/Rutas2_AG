from geopy.geocoders import Nominatim # Para OpenStreetMap
from geopy.exc import GeocoderTimedOut
from geopy.distance import geodesic
from Ag.Interface import Interface as ui
import requests # Para OSRM
import googlemaps

import math

class Model:
    
    geolocator = Nominatim(user_agent="AG_routes")

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
            place_info = (
                place.get("name"),
                place["geometry"]["location"]["lat"], #latitude
                place["geometry"]["location"]["lng"], #longitude
                place.get("vicinity") #address
            )
            places.append(place_info)
        
        return places

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
    def get_distance_and_duration(api_key, origin, destination):
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"
        }
        
        payload = {
            "origin": {"location": {"latLng": {"latitude": origin[0], "longitude": origin[1]}}},
            "destination": {"location": {"latLng": {"latitude": destination[0], "longitude": destination[1]}}},
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE_OPTIMAL"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            try:
                # Verificar si la respuesta contiene las rutas esperadas
                if "routes" in data and len(data["routes"]) > 0:
                    route = data["routes"][0]
                    distance = route["distanceMeters"]
                    duration = route["duration"]
                    return distance, int(duration.split("s")[0])
                else:
                    print("Error: La respuesta no contiene las rutas esperadas.")
                    return None, None
            except KeyError as e:
                print(f"Error al acceder a los datos de la respuesta: {e}")
                return None, None
        else:
            print("Error al obtener la distancia:", response.status_code, response.text)
            return None, None

    @staticmethod
    def get_total_distance_and_duration(api_key, coordinates):
        total_distance = 0
        total_duration = 0
        
        for i in range(len(coordinates) - 1):
            origin = coordinates[i][1:]
            destination = coordinates[i+1][1:]
            distance, duration = Model.get_distance_and_duration(api_key, origin, destination)
            
            if distance is not None and duration is not None:
                total_distance += distance
                total_duration += duration

        return round(total_distance / 1000, 2), round(total_duration / 3600, 2)
    
    @staticmethod

    def harvesine_distance(coord1, coord2):
        R = 6371  # Radio de la Tierra en km

        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

    @staticmethod
    def estimate_travel_time(distance, average_speed=50): #asumiendo una velocidad promedio
        return (distance / average_speed) * 60 #convertir a minutos
