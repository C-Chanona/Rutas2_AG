from geopy.geocoders import Nominatim # Para OpenStreetMap
from Ag.Interface import Interface as ui
import requests
import math
import polyline

class PointOfInterest:
    def __init__(self, name, lat, lon, time):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.visit_time = time

class Model:
    geolocator = Nominatim(user_agent="AG_routes")
    api_key = "AIzaSyDiNQCvlhBC6mxdLF9MXFHXfFflEYuDUGY"

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
    def get_nearby_places(location, place_type, limit=10, radius=5000):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "key": Model.api_key,
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
                    1 #visit_time
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
    def estimate_travel_time(distance, average_speed=80): #asumiendo una velocidad promedio en km/h
        return (distance / average_speed) * 60 #convertir a minutos
        
    @staticmethod
    def get_data_with_api(coordinates):
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": Model.api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
        }

        origin = {"location": {"latLng": {"latitude": coordinates[0][0], "longitude": coordinates[0][1]}}}
        destination = {"location": {"latLng": {"latitude": coordinates[-1][0], "longitude": coordinates[-1][1]}}}
        intermediates = [{"location": {"latLng": {"latitude": lat, "longitude": lng}}} for lat, lng in coordinates[1:-1]]

        payload = {
            "origin": origin,
            "destination": destination,
            "intermediates": intermediates,
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
            "polylineQuality": "HIGH_QUALITY",
            "computeAlternativeRoutes": False,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            },
            "languageCode": "en-US"
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if "routes" in data and len(data["routes"]) > 0:
                route = data["routes"][0]
                distance = route["distanceMeters"] / 1000  # Convertir a kilómetros
                duration = route["duration"]  # Duración en segundos
                polyline_encoded = route["polyline"]["encodedPolyline"]  # Polilínea codificada
                
                return distance, float(duration.split('s')[0]) / 3600  , polyline.decode(polyline_encoded)
            else:
                print("Error: La respuesta no contiene las rutas esperadas.")
                return None, None, None
        else:
            print("Error al obtener la ruta:", response.status_code, response.text)
            return None, None, None
        
    @staticmethod
    def create_path(route):
        ui.map_widget.delete_all_path()
        ui.map_widget.delete_all_marker()
        markers = []
        total_time = 0
        
        for i, poi in enumerate(route['path']):
            total_time += poi.visit_time
            ui.map_widget.set_marker(
                poi.lat, poi.lon, 
                text=f"{i+1}. {poi.name}\n{poi.visit_time:.1f}h", 
                text_color='black', 
                font='Candara 11 bold', 
                marker_color_outside='red', 
                marker_color_circle='brown'
            )
            markers.append((poi.lat, poi.lon))
        
        # Obtener la polilinea con la API de Google Maps
        distance, duration, polyline_encoded = Model.get_data_with_api(markers)
        # Crear la ruta conectando los puntos en orden
        ui.map_widget.set_path(polyline_encoded, name="Tour_Route", color='blue', width=3)
        route['distance'] = distance
        route['duration'] = round(total_time + duration, 2)
        return route