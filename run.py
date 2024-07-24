from Ag.Initialization import Initialization
from Ag.Optimization import Optimization
from Ag.Modeling import Model as md
from Ag.Interface import Interface as ui

def main(country="Mexico", state="Jalisco", city="Guadalaja", days=4, min_places=5, poi_type="park", generation=300):
    init = Initialization(country, state, city, days, poi_type)
    opt = Optimization(min_places, days)

    population = init.generate_population(min_places)
    fitness_results = init.fitness(population)
    best_route = min(fitness_results, key=lambda x: x['fitness'])

    for _ in range(generation):
        selected = opt.selection(fitness_results)
        children = opt.crossover(selected)
        children = opt.mutation(children)
        new_population = list(population) + list(children)
        fitness_results = init.fitness(new_population)
        population, currently_best = opt.poda(fitness_results)
        
        if currently_best['fitness'] < best_route['fitness']:
            best_route = currently_best
    
    route = md.create_path(best_route)
    
    ui.update_table(route)


if __name__ =='__main__':
    ui.create_window(main)
    # main()