import sys
sys.path.append("HyperNetX")
import matplotlib.pyplot as plt
import networkx as nx
import hypernetx as hnx
import warnings
import json


scenes = {
    0: ('FN', 'TH'),
    1: ('TH', 'JV'),
    2: ('BM', 'FN', 'JA'),
    3: ('JV', 'JU', 'CH', 'BM'),
    4: ('JU', 'CH', 'BR', 'CN', 'CC', 'JV', 'BM'),
    5: ('TH', 'GP'),
    6: ('GP', 'MP'),
    7: ('MA', 'GP')
}



H = hnx.Hypergraph(scenes)

print(list(H.nodes))


nodes = list(H.nodes)
num_nodes = len(nodes)
core = {} 
bucket = {} # mapping of number of neighbors, say n, to nodes with exactly n neighbors 


# auxiliary data, that improves efficiency
node_to_neighbors = {} # Not necessary, I guess
node_to_num_neighbors = {} # inverse bucket
removed_nodes = []


# Initial bucket fill-up
for node in nodes:
    neighbors = list(H.neighbors(node))
    len_neighbors = len(neighbors) # this computation can be repeated
    node_to_neighbors[node] = neighbors
    node_to_num_neighbors[node] = len_neighbors
    # print(node, neighbors)
    if(len_neighbors not in bucket):
        bucket[len_neighbors] = [node]
    else:
        bucket[len_neighbors].append(node)

print("\n---------- Initial neighbors -------")
for node in node_to_neighbors:
    print(node, node_to_neighbors[node])
print()


print("\n---------- Initial bucket -------")
print(bucket)
print()

for k in range(1, num_nodes + 1):
    
    # TODO Discuss with Naheed vai about this case
    if(k not in bucket):
        continue

    

    # Inner while loop
    assert k in bucket
    while len(bucket[k]) != 0:
        v = bucket[k].pop(0) # get first element in the
        print("k:", k, "node:", v)
        core[v] = k
        temp_nodes = nodes.copy()
        temp_nodes.remove(v) # V' <- V \ {v}
        removed_nodes.append(v)
        # print(nodes)


        # enumerating over all neighbors of v
        for u in node_to_neighbors[v]:

            """
                In each iteration, v is removed. Therefore, node_to_neighbors has to be updated too. 
                Alternate implementation is to only consider remaining neighbors of v that are not yet removed.
            """
            if(u in removed_nodes):
                continue


            print(node_to_num_neighbors)


            H_temp = H.restrict_to_nodes(temp_nodes)
            print("Considering neighbor", u)
            neighbors_u = list(H_temp.neighbors(u))
            len_neighbors_u = len(neighbors_u) # repeated computaion, hence a variable is declared
            print(u, 'has neighbors on sub-hypergraph:', neighbors_u)

            max_value = max(len_neighbors_u, k)
            print("max core between", k, 'and',len_neighbors_u, "is ", max_value)
            print("The location of", u, "is updated from", node_to_num_neighbors[u], "to", max_value)
            bucket[node_to_num_neighbors[u]].remove(u)
            
            # Move u to new location in bucket
            if(max_value not in bucket):
                #TODO does code reach here?
                bucket[max_value] = [u]
            else:
                bucket[max_value].append(u)
            
            # update new location of u
            node_to_num_neighbors[u] = max_value

            print("-------- Updated bucket ---------")
            print(bucket)
            print()
        
        nodes = temp_nodes


print("\n\nOutput")
print(core)
    
    





