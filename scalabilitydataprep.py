from hgDecompose.utils import get_hg, writeHypergraphHg, writeHypergraph, get_random_hg
from hgDecompose.Hypergraph import Hypergraph
import random,os
import time 
from matplotlib import pyplot as plt
# random.seed(10)

def gen_nested_hypergraph(num_subgraphs = 10):
    delete_percent = 1.0/num_subgraphs
    
    name = "dblp"
    input_H = get_hg(name) 
    pathstring = "/Users/nus/hg-core-decomposition/data/datasets/scalability/"

    sub_hg_edges = {}
    M = 0
    eids = []
    for e_id, hyperedge in input_H.edge_eid_iterator():
        sub_hg_edges[e_id] = tuple(hyperedge)
        M+=1
        eids.append(e_id)

    todelete = int(M * delete_percent)
    writeHypergraph(sub_hg_edges, os.path.join(pathstring,name+"_"+str(0)+".hyp"))
    print("0: NumEdge: ", len(sub_hg_edges))
    random.shuffle(eids)
    del input_H 
    # del sub_hg_edges

    for i in range(num_subgraphs-1):
        # M = len(sub_hg_edges)
        print(i,' - ',todelete)
        # eids = list(sub_hg_edges.keys())
        # sample = random.sample(eids, k=round(M-todelete))
        # for e_id in eids: 
        #     if e_id not in sample:
        #         del sub_hg_edges[e_id]
        for e_id in eids[-todelete:]:
            # e_id = eids[i]
            if e_id in sub_hg_edges:
                del sub_hg_edges[e_id]
        print(str(i+1)+ ": NumEdge: ", len(sub_hg_edges))
        writeHypergraph(sub_hg_edges, os.path.join(pathstring,name+"_"+str(i+1)+".hyp"))
        todelete = todelete + int(M*delete_percent)
    
def getrepr(edge):
    edge_str = ",".join([str(node) for node in edge])
    return edge_str+"\n"

def writerepr(string_rep, fileHandle):
    fileHandle.write(string_rep)

def hg_preferential_attach(p, initial_hg, uniform = True, parallel_edge_allowed = False, seed = 1, writeHandle = None):
    """ 
        # N => maximum number of vertices, 
        p => p in the paper,
        initial_hg => Initial hypergraph where preferentially attach new vertices and hyperedges.
    """
    assert isinstance(initial_hg, Hypergraph)
    random.seed(seed)
    t = 1
    new_vid = 0 # New vertices added would have id starting from new_vid
    for u in initial_hg.init_nodes:
        new_vid = max(new_vid, int(u) + 1) 
    
    new_eid = 0 # New hyperedges added would have id starting from new_eid
    for e_id in initial_hg.e_indices.keys():
        new_eid = max(new_eid, int(e_id) + 1) 

    if (uniform):
        e_id = list(initial_hg.e_indices.keys())[0]
        e = initial_hg.get_edge_byindex(e_id)
        size_e = len(e)

    while True:
        if not (uniform):
            # select a random size for the new hyperedge. Upper-bound= current |V|, lower-bound = 1
            size_e = random.randint(1, initial_hg.get_N())
        r = random.random()
        if r < p:
            e = [str(new_vid)]
            # sample size_e - 1 vertices from existing Hg 
            for u in initial_hg.sample_v_preferential_attachment(size_e - 1):
                e.append(u)
            e = tuple(sorted(e))
            if parallel_edge_allowed:
                initial_hg.add_edge(e_id = new_eid,e_nodes = e)
                rep = getrepr(e)
                yield (t, rep, initial_hg)
                new_eid += 1
                new_vid += 1
                t += 1
            else:
                if not initial_hg.hasEdge(e):
                    initial_hg.add_edge(e_id = new_eid,e_nodes = e)
                    rep = getrepr(e)
                    yield (t, rep, initial_hg)
                    new_eid += 1
                    new_vid += 1
                    t += 1
                else:
                    t += 1
        else:
            # sample size_e vertices from existing Hg 
            e = []
            for u in initial_hg.sample_v_preferential_attachment(size_e):
                e.append(u)
            e = tuple(sorted(e))
            if parallel_edge_allowed:
                initial_hg.add_edge(e_id = new_eid,e_nodes = e)
                rep = getrepr(e)
                yield (t, rep, initial_hg)
                new_eid += 1
                t += 1
            else:
                # print(e, initial_hg.hasEdge(e))
                if not initial_hg.hasEdge(e):
                    initial_hg.add_edge(e_id = new_eid,e_nodes = e)
                    rep = getrepr(e)
                    yield (t, rep, initial_hg)
                    new_eid += 1
                    t += 1
                else:
                    t += 1

def get_initial_hg(n = 10, m = 5, edge_size_ub = None, parallel_edge_allowed = False, seed = 10):
    """ 
    Returns an initial random hypergraph with m edges, n vertices
    Each edge has cardinality at most edge_size_ub and at least 2.
    """
    return get_random_hg(n,m,edge_size_ub, seed)

def gen_Random_zipf(max_num_edges = 2, seed = 1, parallel_edge_allowed = False, write = True):
    """ Preferential attachment model """
    p = 0.2
    path = 'data/datasets/scalability/'
    print('seed: ',seed)
    kuniform = 3
    initial_hg = get_initial_hg(kuniform, 1, kuniform, seed = seed) # Start with 1 edge.
    print("Initial Hg: ",initial_hg)

    if parallel_edge_allowed:
        out_file = os.path.join(path,"pref_"+str(max_num_edges)+"_"+str(kuniform)+"_"+str(seed)+".hyp")
    else:
        out_file = os.path.join(path,"pref_"+str(max_num_edges)+"_"+str(kuniform)+"_"+str(seed)+"_simple.hyp")
    # Writer code
    writeHandle = open(out_file,'a')
    for id in sorted(list(initial_hg.e_indices.keys())):
        edge = initial_hg.get_edge_byindex(id)
        rep = getrepr(edge)
        writerepr(rep, writeHandle)
    
    num_e = 1
    writeInterval = 1000
    repr = ""
    if max_num_edges>=2:
        for t, e_str, _ in hg_preferential_attach(p = p, initial_hg = initial_hg, parallel_edge_allowed = parallel_edge_allowed, seed = seed, writeHandle = writeHandle):
            # print(t)
            # print(hg)
            # print('-----')
            
            if num_e % writeInterval == 0:
                writerepr(repr, writeHandle)
                repr = ""
            else:
                repr += e_str 
            
            if num_e >= max_num_edges-1:
                if len(repr):
                    writerepr(repr, writeHandle)
                break
            num_e += 1
    writeHandle.close()
    if parallel_edge_allowed:
        degdistf = os.path.join(path,"degdist_"+str(max_num_edges)+"_"+str(kuniform)+"_"+str(seed))
    else:
        degdistf = os.path.join(path,"degdist_"+str(max_num_edges)+"_"+str(kuniform)+"_"+str(seed)+"_simple")
    initial_hg.WriteDegreeDist(filename = degdistf)
    return initial_hg

def gen_Random_zipf_H0(initial_hg_name, max_num_edges = 10, seed = 1, parallel_edge_allowed = False, write = True):
    """ Preferential attachment model """
    p = 0.2
    path = 'data/datasets/scalability/'
    print('seed: ', seed)
    kuniform = 3
    initial_hg = get_hg(initial_hg_name) # Make sure this is kuniform
    print("Initial Hg: ",initial_hg_name)

    if parallel_edge_allowed:
        out_file = os.path.join(path,"pref_"+str(max_num_edges)+"_"+str(kuniform)+"_"+str(seed)+".hyp")
    else:
        out_file = os.path.join(path,"pref_"+str(max_num_edges)+"_"+str(kuniform)+"_"+str(seed)+"_simple.hyp")
    # Writer code
    writeHandle = open(out_file,'a')
    repr = ""
    num_e = 0
    for id in initial_hg.e_indices.keys():
        edge = initial_hg.get_edge_byindex(id)
        repr += getrepr(edge)
        num_e += 1
    writeInterval = 1000

    if max_num_edges>=2:
        for t, e_str, _ in hg_preferential_attach(p = p, initial_hg = initial_hg, parallel_edge_allowed = parallel_edge_allowed, seed = seed, writeHandle = writeHandle):
            # print(t)
            # print(hg)
            # print('-----')
            
            if num_e % writeInterval == 0:
                writerepr(repr, writeHandle)
                repr = ""
            else:
                repr += e_str 
            
            if num_e >= max_num_edges-1:
                if len(repr):
                    writerepr(repr, writeHandle)
                break
            num_e += 1
    writeHandle.close()
    if parallel_edge_allowed:
        degdistf = os.path.join(path,"degdist_"+str(max_num_edges)+"_"+str(kuniform)+"_"+str(seed))
    else:
        degdistf = os.path.join(path,"degdist_"+str(max_num_edges)+"_"+str(kuniform)+"_"+str(seed)+"_simple")
    initial_hg.WriteDegreeDist(filename = degdistf)
    return initial_hg

def plot_cdf(x, y):
    import numpy as np
    import scipy
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # print(x)
    # print(y)
    # y = np.cumsum(y)
    # print(y)
    # plot the cdf
    # plt.plot(np.log(x), np.log(y))
    plt.loglog(x,y)
    # plt.bar(x,y)
    plt.show()


def plot_dataset(hg):
    X = []
    Y = []
    for x, freq in  hg.get_degree_distr():
        X.append(x)
        Y.append(freq)
    plot_cdf(X, Y)

def plot_two_dataset(hg, rhg):
    X = []
    Y = []
    for x, freq in  hg.get_degree_distr():
        X.append(x)
        Y.append(freq)
    plt.loglog(X,Y,label = 'baseline')
    X = []
    Y = []
    for x, freq in  rhg.get_degree_distr():
        X.append(x)
        Y.append(freq)
    plt.loglog(X,Y,label = 'random')
    plt.legend()
    plt.show()


# # seed = int(time.time())
# # seed = 1634545894
# seed = 1
# name = 'enron'
# # hg = get_hg(name)
# # # plot_dataset(hg)
# # M = hg.get_M()
# M = 20000
# issimpleHg = True 
# # M = 100
# rhg = gen_Random_zipf(M, seed = seed, parallel_edge_allowed = (not issimpleHg), write = True)
# plot_dataset(rhg)
# # writeHypergraphHg(rhg,out_file = 'data/datasets/scalability/3pref_'+str(seed)+"_"+str(M)+'.hyp')
# # plot_two_dataset(hg,rhg)
# # print("Final hypergraph: ")
# # print(hg)

# gen_Random_zipf_H0("pref_80000", max_num_edges = 100000, seed = 1, parallel_edge_allowed = False, write = True)
gen_nested_hypergraph()