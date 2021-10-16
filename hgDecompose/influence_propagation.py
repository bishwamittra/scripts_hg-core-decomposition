import random
import numpy as np


def propagate_for_all_vertices(H, core, num_vertex_per_core = 100, top_k = 100,  p = 0.5, num_iterations = 10, verbose=True):


    
    result = {} # Entry is a core number. value is a list of percentages of the infected population for all vertices with the same core number


    core_to_vertex_map = {}
    distinct_core_numbers = []
    for v in core:
        if(core[v] not in core_to_vertex_map):
            core_to_vertex_map[core[v]] = [v]
            distinct_core_numbers.append(core[v])
        else:
            core_to_vertex_map[core[v]].append(v)

    distinct_core_numbers.sort(reverse=True)


    for core_number in distinct_core_numbers[:top_k]:
        for v in random.choices(core_to_vertex_map[core_number], k=num_vertex_per_core):
            if(core_number not in result):
                result[core_number] = [propagate(H, starting_vertex=v, p = p, num_iterations = num_iterations, verbose = verbose)[0]]
            else:
                result[core_number].append(propagate(H, starting_vertex=v, p = p, num_iterations = num_iterations, verbose = verbose)[0])
            

    return result, None

def propagate_for_random_seeds(H, core, seed_size = 1000, p = 0.5, num_iterations = 10, verbose = False):

    # print(core)
    result = {}
    # 
    for v in random.choices(H.nodes(), k = seed_size):
        # print(v)
        _, timestep_of_infection = propagate(H, starting_vertex = v, p = p, num_iterations = num_iterations, verbose = False)
        # print(timestep_of_infection)
        # print()
        for u in timestep_of_infection:
            if(core[u] not in result):
                result[core[u]] = [timestep_of_infection[u]]
            else:
                result[core[u]].append(timestep_of_infection[u])

    # print(result)

    return None, result



def propagate(H, starting_vertex, p = 0.5, num_iterations = 10, verbose=True):
    """
    """
    
    timestep_of_infection = {}
    len_nodes = H.get_N()
    for v in H.nodes():
        timestep_of_infection[v] = len_nodes - 1 
    suscepted = H.nodes()
    suscepted.remove(starting_vertex)
    infected = [starting_vertex]
    timestep_of_infection[starting_vertex] = 0
    recovered = []

    for i in range(num_iterations):
        if(verbose):
            print('\n\n\nIteration:', i)
            print("infected:", infected)
            print("recovered:", recovered)
            print("suscepted:", suscepted)
            print()
        
        if(len(infected) == 0):
            if(verbose):
                print("No more propagation is possible")
            break
        
        
        new_infected = []
        new_recovered = []    
        for v in infected:
            if(verbose):
                print("\nPorpagating for", v)
            for u in H.neighbors(v):
                if(u in suscepted):
                    if(random.random() <= p):
                        if(verbose):
                            print(v, "->", u)
                        new_infected.append(u)
                        timestep_of_infection[u] = i + 1
                        suscepted.remove(u)
                    else:
                        if(verbose):
                            print(v, "->", u, "not propagated")
                # else:
                #     if(verbose):
                #         print(u, "is already either infected or recovered")
            new_recovered.append(v)


        infected += new_infected
        recovered += new_recovered
        for v in new_recovered:
            infected.remove(v)
    
    return 1 - float(len(suscepted) / H.get_N()), timestep_of_infection
