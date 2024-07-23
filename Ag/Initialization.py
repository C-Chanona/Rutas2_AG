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
        self.api_key = "AIzaSyDiNQCvlhBC6mxdLF9MXFHXfFflEYuDUGY"
        self.route_cache = {}
        self.route_evaluations = {}

    def generate_population(self, max_places, p0=10):
        address = f'{self.city}, {self.state}, {self.country}' if self.state else f'{self.city}, {self.country}'
        self.center = md.name_to_coordinates(address)

        if not self.center:
            print("No se pudo encontrar la ubicación especificada. Por favor, intenta de nuevo.")
            return "No se pudo encontrar la ubicación especificada. Por favor, intenta de nuevo."
        
        places = md.get_nearby_places(self.api_key, self.center, self.poi_type)

        population = []
        for _ in range(p0):
            route = random.sample(places, max_places)
            population.append(route)

        return population
    
    def fitness(self, population):
        population_with_fitness = []

        for route in population:
            route_key = tuple(poi.name for poi in route) #Si la ruta ya ha sido evaluada, usar resultados directamente
            
            if route_key in self.route_evaluations:
                total_duration, total_distance, path = self.route_evaluations[route_key]
            else:
                total_duration = 0
                total_distance = 0
                
                path, total_distance, total_duration = md.run_path(route)
            
            self.route_evaluations[route_key] = (total_duration, total_distance, path)
            
            population_with_fitness.append({
                'route': route,
                'fitness': total_distance,
                'duration': total_duration,
                'path': path,
            })

        return population_with_fitness

    # def fitness(self, population):
    #     population_with_fitness = []

    #     for route in population: # Evaluacion por lotes
    #         route_key = tuple(poi[0] for poi in route) #usa el nombre de los POI como clave
            
    #         if route_key in self.route_evaluations: # Si una ruta completa ya ha sido evaluada, usamos esos resultados directamente.
    #             total_duration, total_distance, poi_count = self.route_evaluations[route_key]
    #         else: # Para rutas nuevas o modificadas, se evalua solo los segmentos que han cambiado.
    #             total_duration = 0
    #             total_distance = 0
    #             previous_poi = self.center
    #             poi_count = len(route)

    #             for poi in route:
    #                 poi_coords = (poi[1], poi[2])
    #                 segment_key = (previous_poi, poi_coords)

    #                 if segment_key in self.route_cache:
    #                     # Este segmento no ha cambiado, usar valores cacheados
    #                     distance, duration = self.route_cache[segment_key]
    #                 else:
    #                     # Segmento cambiado, evaluar y marcar para actualización
    #                     distance, duration = self.evaluate_segment(previous_poi, poi_coords)
    #                     self.route_cache[segment_key] = (distance, duration) # Actualizar cache inmediatamente

    #                 total_duration += duration  # Ahora duration es un entero (minutos)
    #                 total_distance += distance
                    
    #                 # Añadir tiempo estimado de visita al POI (por ejemplo, 2 horas)
    #                 visit_time = 120  # 2 horas en minutos
    #                 total_duration += visit_time

    #                 previous_poi = poi_coords #Actualizar para el proximo segmento
            
    #             #guardar evaluacion completa de la ruta
    #             self.route_cache[route_key] = (total_duration, total_distance, poi_count)
            
    #        # Calcular penalizaciones y fitness
    #         penalty = 0
    #         if total_duration > self.minutes:
    #             penalty += (total_duration - self.minutes) * 10
    #         if total_duration < self.minutes * 0.7:
    #             penalty += (self.minutes * 0.7 - total_duration) * 5
            
    #         poi_bonus = poi_count * 50
    #         fitness_value = (total_duration + total_distance + penalty - poi_bonus) / poi_count
    #         fitness_value = round(fitness_value, 2)
            
    #         population_with_fitness.append({
    #             'route': route,
    #             'fitness': fitness_value,
    #             'duration': total_duration,
    #             'distance': total_distance,
    #             'penalty': penalty,
    #             'poi_count': poi_count
    #         })

    #     return population_with_fitness
    
    # def evaluate_segment(self, start, end): #Cache de resultados
    #     cache_key = (start, end)
    #     if cache_key in self.route_cache: # Si el segmento actual ya fue evaluado anteriormente, usar valores de la cache en vez de volverlos a calcular
    #         return self.route_cache[cache_key]
    #     else:
    #         distance = md.harvesine_distance(start, end)
    #         duration = md.estimate_travel_time(distance)
    #         self.route_cache[cache_key] = (distance, duration) # Actualizar el segmento en cache inmediatamente
    #         return distance, duration