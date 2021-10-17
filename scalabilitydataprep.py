from hgDecompose.utils import get_hg, writeHypergraph
from hgDecompose.Hypergraph import Hypergraph
import random,os
random.seed(10)

def gen_nested_hypergraph():
    percent = 0.8
    num_subgraphs = 10
    name = "dblp"
    input_H = get_hg(name)
    pathstring = "/Users/nus/hg-core-decomposition/data/datasets/scalability/"

    sub_hg_edges = {}
    for e_id, hyperedge in input_H.edge_eid_iterator():
        sub_hg_edges[e_id] = tuple(hyperedge)
    writeHypergraph(sub_hg_edges, os.path.join(pathstring,name+"_"+str(0)+".hyp"))
    print("0: NumEdge: ", len(sub_hg_edges))
    del input_H
    for i in range(num_subgraphs):
        M = len(sub_hg_edges)
        eids = list(sub_hg_edges.keys())
        sample = random.sample(eids, k=round(M * percent))
        for e_id in eids: 
            if e_id not in sample:
                del sub_hg_edges[e_id]
        print(str(i+1)+ ": NumEdge: ", len(sub_hg_edges))
        writeHypergraph(sub_hg_edges, os.path.join(pathstring,name+"_"+str(i+1)+".hyp"))
    
def gen_Random_zipf():
    """ Preferential attachment model """
    pass 