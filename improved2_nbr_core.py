import sys
import matplotlib
matplotlib.use('TkAgg')
sys.path.append("HyperNetX")
import hypernetx as hnx
import math
from copy import deepcopy
from hgDecompose import utils

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

# # Visualise hypergraph for verification purposes
# hnx.drawing.draw(H,with_edge_labels = False, layout_kwargs = {'seed': 39})
# plt.savefig('test.pdf')


nodes = list(H.nodes)
num_nodes = len(nodes)
core = {} 
bucket = {}  # mapping of number of neighbors, say n, to nodes with exactly n neighbors

# auxiliary data, that improves efficiency
# node_to_neighbors = {} # Not necessary, I guess
node_to_num_neighbors = {} # inverse bucket
# removed_nodes = []

glb = math.inf
llb = {}
gub = -math.inf
lub = {}
# flag = {}
# Initial bucket fill-up
for node in nodes:
    nbrs = H.neighbors(node)
    # neighbors = list(H.neighbors(node))
    len_neighbors = len(nbrs) # this computation can be repeated
    glb = min(glb,len_neighbors)
    gub = max(gub,len_neighbors)
    # LB2 computation
    for u in nbrs:
        llb[node] = min(llb.get(node,len_neighbors),len(H.neighbors(u))-1)
    # node_to_neighbors[node] = neighbors
    node_to_num_neighbors[node] = len_neighbors
    # print(node, neighbors)
    if len_neighbors not in bucket:
        bucket[len_neighbors] = [node]
    else:
        bucket[len_neighbors].append(node)
    # flag[node] = False


print("\n---------- Initial neighbors -------")
for node in H.nodes:
    print(node, H.neighbors(node))
print()


print("\n---------- Initial bucket -------")
print(bucket)
print()

# Compute Local upper bounds
copy_bucket = deepcopy(bucket)
inv_bucket = deepcopy(node_to_num_neighbors)

for k in range(glb, gub):
    while len(copy_bucket.get(k, []))!=0:
        v = copy_bucket[k].pop(0)
        lub[v] = k
        for u in utils.get_nbrs(H,v):
            if u not in lub:
                max_value = max(inv_bucket[u]-1, k)
                copy_bucket[inv_bucket[u]].remove(u)
                copy_bucket[max_value].append(u)
                inv_bucket[u] = max_value
                # if inv_bucket[u] > k:
                #     copy_bucket[inv_bucket[u]].remove(u)
                #     inv_bucket[u] -=1
                #     copy_bucket[inv_bucket[u]].append(u)
                # else:
                #     pass
# for k in range(lb1, ub1):
#     while len(bucket.get(k, [])) != 0:
#         v = bucket[k].pop(0) # get first element in the
#         print("k:", k, "node:", v)
#         core[v] = k
#
#         temp_nodes = nodes[:] # Make a copy of nodes
#         temp_nodes.remove(v)  # V' <- V \ {v}
#         H_temp = utils.strong_subgraph(H, temp_nodes)
#         for u in utils.get_nbrs(H, v):
#
#             if lb2[u] <= k:
#                 len_neighbors_u = utils.get_number_of_nbrs(H_temp, u)
#
#                 max_value = max(len_neighbors_u, k)
#                 print("max core between", k, 'and', len_neighbors_u, "is ", max_value)
#                 print("The location of", u, "is updated from", node_to_num_neighbors[u], "to", max_value)
#                 bucket[node_to_num_neighbors[u]].remove(u)
#                 bucket[max_value].append(u)
#
#                 # update new location of u
#                 node_to_num_neighbors[u] = max_value
#
#             print("-------- Updated bucket ---------")
#             print(bucket)
#             print()
#         nodes = temp_nodes
#         H = H_temp
print('local upper bound: ')
print(sorted(lub.items()))
print('local lower bound: ')
print(sorted(llb.items()))
print("\n\nOutput")
print(core)