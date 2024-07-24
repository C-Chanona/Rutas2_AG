import random
from Ag.Modeling import Model as md

class Initialization:
    def __init__(self, country, state, city, days, poi_type):
        self.country = country
        self.state = state
        self.city = city
        self.days = days
        self.hours = (days * 24) - (12 * days) # Suponiendo 8 horas de sueño y 4 horas de comida
        self.minutes = self.hours * 60
        self.poi_type = poi_type
        self.route_cache = {}
        self.route_evaluations = {}

    def generate_population(self, max_places, p0=10):
        address = f'{self.city}, {self.state}, {self.country}' if self.state else f'{self.city}, {self.country}'
        self.center = md.name_to_coordinates(address)

        if not self.center:
            print("No se pudo encontrar la ubicación especificada. Por favor, intenta de nuevo.")
            return "No se pudo encontrar la ubicación especificada. Por favor, intenta de nuevo."
        
        places = md.get_nearby_places(self.center, self.poi_type)

        population = []
        for _ in range(p0):
            route = random.sample(places, max_places)
            population.append(route)

        return population

    def fitness(self, population):
        population_with_fitness = []
        max_allowed_time = 12 * 60  # 12 horas en minutos

        for route in population:
            route_key = tuple(poi.name for poi in route)
            
            if route_key in self.route_evaluations:
                total_duration, total_distance, path = self.route_evaluations[route_key]
            else:
                path, total_distance, total_duration = md.run_path(route)
            
            self.route_evaluations[route_key] = (total_duration, total_distance, path)
            
            # Calcular fitness
            if total_duration <= max_allowed_time:
                # Si está dentro del límite de tiempo, el fitness es simplemente la distancia total de la ruta
                fitness_value = total_distance
            else:
                # Si la ruta excede el límite de tiempo, penalizamos fuertemente su fitness
                fitness_value = total_distance * (1 + (total_duration - max_allowed_time) / max_allowed_time)
            
            population_with_fitness.append({
                'route': route,
                'fitness': fitness_value,
                'duration': total_duration,
                'distance': total_distance,
                'path': path,
            })

        return population_with_fitness