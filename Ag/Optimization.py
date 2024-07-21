import random
from Ag.Modeling import Model as md

class Optimization:
    def __init__(self, max_places):
        self.max_places = max_places

    def selection(self, population_with_fitness):
        selected = []
        for _ in range(len(population_with_fitness)):
            tournament = random.sample(population_with_fitness, min(3, len(population_with_fitness)))
            winner = min(tournament, key=lambda x: x['fitness'])
            selected.append(winner['route'])
        return selected
    
    def crossover(self, selected):
        children = []
        random.shuffle(selected)  # Mezclar la lista para emparejar aleatoriamente
        
        for i in range(0, len(selected) - 1, 2):
            first_route = selected[i]
            second_route = selected[i + 1]
            
            if len(first_route) > 1 and len(second_route) > 1:
                crossover_point = random.randint(1, min(len(first_route), len(second_route)) - 1)
                son = first_route[:crossover_point] + [x for x in second_route if x not in first_route[:crossover_point]]
                daughter = second_route[:crossover_point] + [x for x in first_route if x not in second_route[:crossover_point]]
                
                children.append(son)
                children.append(daughter)
        
        return children
    
    def mutation(self, children):
        for i in range(len(children)):
            if random.random() < 0.1:  # Probabilidad de mutación
                if len(children[i]) >= 2:
                    start, end = sorted(random.sample(range(len(children[i])), 2))
                    children[i][start:end+1] = reversed(children[i][start:end+1])
        return children

    def poda(self, population_with_fitness):
        sorted_population = sorted(population_with_fitness, key=lambda x: x['fitness'])
        elite_size = min(self.max_places // 2, len(sorted_population))
        next_generation = [route['route'] for route in sorted_population[:elite_size]]
        
        while len(next_generation) < self.max_places and len(next_generation) < len(population_with_fitness):
            random_individual = random.choice(population_with_fitness)
            if random_individual['route'] not in next_generation:
                next_generation.append(random_individual['route'])
        
        return next_generation