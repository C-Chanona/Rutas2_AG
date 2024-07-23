from Ag.Initialization import Initialization
from Ag.Optimization import Optimization
from Ag.Interface import Interface as ui

def main(country="Mexico", state="Chiapas", city="Tuxtla Gutierrez", days=4, max_places=5, poi_type="park"):
    init = Initialization(country, state, city, days, poi_type)
    opt = Optimization(max_places, days)

    population = init.generate_population(max_places)
    fitness_results = init.fitness(population)
    best_route = min(fitness_results, key=lambda x: x['fitness'])
    # ui.create_path(best_route['path'])

    for _ in range(100):
        selected = opt.selection(fitness_results)
        children = opt.crossover(selected)
        children = opt.mutation(children)
        new_population = list(population) + list(children)
        fitness_results = init.fitness(new_population)
        currently_best = min(fitness_results, key=lambda x: x['fitness'])
        population = opt.poda(fitness_results)
        if currently_best['fitness'] < best_route['fitness']:
            best_route = currently_best
        # print("POBLACION PODADA \n \n", population)
    
    print("MEJOR RUTA \n", population[0])
    ui.create_path(population[0])
    # ui.create_path(best_route['path'])


if __name__ =='__main__':
    ui.create_window(main)
    # main()