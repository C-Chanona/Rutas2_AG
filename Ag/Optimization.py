import random
from Ag.Modeling import Model as md

class Optimization:
    def __init__(self, max_places, days):
        self.max_places = max_places
        self.days = days
    
    def selection(self, population_with_fitness):
        selected = []
        parents = []

        for _ in range(len(population_with_fitness)):
            tournament = random.sample(population_with_fitness, min(self.max_places, len(population_with_fitness)))
            winner = min(tournament, key=lambda x: x['fitness'])
            selected.append(winner['route'])
        
        while len(selected) >= 2:
            first_route = random.choice(selected)
            selected.remove(first_route)
            second_route = random.choice(selected)
            selected.remove(second_route)
            parents.append((first_route, second_route))

        return parents
    
    def crossover(self, selected):
        childrens = []
        for parent1, parent2 in selected:
            start = random.randint(0, len(parent1)-1)
            end = random.randint(start+1, len(parent1))
            child = parent1[start:end]
            child += [poi for poi in parent2 if poi not in child]
            childrens.append(child)
        
        return childrens
    
    def mutation(self, childrens):
        print("MUTACION", childrens)
        for children in childrens:
            if random.random() > 0.3:
                i, j = random.sample(range(len(children)), 2)
                children[i], children[j] = children[j], children[i]
        return childrens
    
    def poda(self, population_with_fitness):
        sorted_population = sorted(population_with_fitness, key=lambda x: x['fitness'])
        best_route = sorted_population[0]
        next_generation = [best_route['path']]
        
        # Selecciona el resto de individuos aleatoriamente
        while len(next_generation) < self.max_places:
            random_individual = random.choice(population_with_fitness)
            next_generation.append(random_individual['path'])
        
        return next_generation