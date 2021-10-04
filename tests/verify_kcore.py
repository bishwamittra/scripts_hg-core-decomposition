from hgDecompose.Hypergraph import Hypergraph
import math 

def construct_subgraph_from_core_number(H, k, cores):
    """ 
    Construct subgraph k-core of H from threshold => k, given cores => dictionary of cores-computed
    """
    edges = {}
    for e_id, e in H.edge_eid_iterator():
        flag = True 
        for v in e:
            if cores[v] < k:
                flag = False 
                break 
        if flag:
            edges[e_id] = e 
    return Hypergraph(_edgedict = edges)

def verify_subgraph(H, threshold, cores):
    """
    Given a core-assignment, and threshold k, verify whether the k-core has indeed the following property:=>
        every vertex in the subgraph (k-core) has at least $k$ neighbours in the k-core.
    """
    assert isinstance(H, Hypergraph)
    k_core = construct_subgraph_from_core_number(H, k = threshold, cores=cores)
    # print(k_core.inc_dict)
    flag = 1 # Passed
    for v in k_core.node_iterator():
        if k_core.get_init_nbrlen(v) >= cores[v]:
            pass 
        else:
            print('node: ',v)
            print('nbrs in k-core: ',k_core.get_init_nbrlen(v), ' original nbrs: ',H.get_init_nbrlen(v))
            print(H.get_init_nbrlen(v), ' ', k_core.get_init_nbrlen(v))
            print("nbrs of v in original hypergraph that are less than its core_number:", cores[v])
            for u in H.get_init_nbr(v):
                if cores[u] < cores[v]:
                    print(u, ' ',cores[u])
            flag = 0 # Test failed
            break 
    print(["Verification False","Verification True"][flag])

