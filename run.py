from Ag.Initialization import Initialization
from Ag.Optimization import Optimization
from Ag.Interface import Interface as ui

def main(country, state, city, days, max_places, poi_type):
    init = Initialization(country, state, city, days, poi_type)
    opt = Optimization(max_places)

    population = init.generate_population(max_places)
    print("POBLACION INICIAL \n", population)
    fitness_results = init.fitness(population)
    for _ in range(200):
        selected = opt.selection(fitness_results)
        # print("SELECCIONADOS \n", selected)
        children = opt.crossover(selected)
        # print("HIJOS \n", children)
        children = opt.mutation(children)
        # print("HIJOS MUTADOS \n", children)
        # children = [opt.local_optimization(child) for child in children]
        new_population = list(population) + list(children)
        # print("NUEVA POBLACION \n", new_population)
        fitness_results = init.fitness(new_population)
        population = opt.poda(fitness_results)
        # print("POBLACION PODADA \n \n", population)
    
    print("MEJOR RUTA \n", population[0])
    ui.create_path(population[0])


if __name__ =='__main__':
    ui.create_window(main)