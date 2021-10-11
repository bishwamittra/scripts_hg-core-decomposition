import random


def propagate(H, starting_vertex, p = 0.5, verbose=True):
    """
    """

    random.seed(10)
    suscepted = H.nodes()
    suscepted.remove(starting_vertex)
    infected = [starting_vertex]
    recovered = []

    for i in range(10):
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
                    if(random.random() > 0.55):
                        if(verbose):
                            print(v, "->", u)
                        new_infected.append(u)
                        suscepted.remove(u)
                    else:
                        if(verbose):
                            print(v, "->", u, "not propagated")
                else:
                    if(verbose):
                        print(u, "is already either infected or recovered")
            new_recovered.append(v)


        infected += new_infected
        recovered += new_recovered
        for v in new_recovered:
            infected.remove(v)
        
