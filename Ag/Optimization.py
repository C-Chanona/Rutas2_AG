import random
from Ag.Modeling import Model as md

class Optimization:
    def __init__(self, min_places, days):
        self.min_places = min_places
        self.days = days
    
    def selection(self, population_with_fitness):
        selected = []
        parents = []

        for _ in range(len(population_with_fitness)):
            tournament = random.sample(population_with_fitness, min(self.min_places, len(population_with_fitness)))
            winner = min(tournament, key=lambda x: x['fitness'])
            selected.append(winner['route'])
        
        while len(selected) >= 2:
            first_route = random.choice(selected)
            selected.remove(first_route)
            second_route = random.choice(selected)
            selected.remove(second_route)
            parents.append((first_route, second_route))
        
        return parents
    
    def crossover(self, selected): # cruce de orden parcial (Partially Mapped Crossover, PMX)
        childrens = []
        for parent1, parent2 in selected:
            start = random.randint(0, len(parent1)-1)
            end = random.randint(start+1, len(parent1))
            child = parent1[start:end]
            child += [poi for poi in parent2 if poi not in child]
            childrens.append(child)
        
        return childrens
    
    def mutation(self, childrens):
        for children in childrens:
            if random.random() > 0.2:
                i, j = random.sample(range(len(children)), 2)
                children[i], children[j] = children[j], children[i]
                for poi in children:
                    if random.random() > 0.4:
                        poi.visit_time = max(0.5, min(3, poi.visit_time + random.uniform(-0.5, 0.5))) #Mantiene el tiempo de visita entre 0.5 y 3 horas

        return childrens
    
    def poda(self, population_with_fitness):
        sorted_population = sorted(population_with_fitness, key=lambda x: x['fitness'])
        best_route = sorted_population[0]
        next_generation = [best_route['route']]
        
        # Selecciona el resto de individuos aleatoriamente
        while len(next_generation) < self.days:
            random_individual = random.choice(population_with_fitness)
            next_generation.append(random_individual['route'])
        
        return next_generation, best_route