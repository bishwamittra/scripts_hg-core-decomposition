import sys

sys.path.append("HyperNetX")
import hypernetx as hnx
import pandas as pd



def strong_subgraph(H, vertex_set):
    """
    Returns the strong sub-hypergraph of H induced by vertex_set
    Parameters
    ----------
    H: Hypernetx Hypergraph
    vertex_set: List/set of vertex label

    Returns
    -------
    Hypernetx Hypergraph object
        The strong sub-hypergraph induced by vertex_set
    """
    assert isinstance(H, hnx.Hypergraph)
    if not isinstance(vertex_set, set):
        X = set(vertex_set)
    else:
        X = vertex_set
    _tempdict = {}  # dictionary for induced edges
    for e_id, e_i in H.incidence_dict.items():
        set_e = set(e_i)
        if set_e.issubset(X):  # If an edge of the original hypergraph is a subset of the vertex set, add it
            _tempdict[e_id] = e_i
    return hnx.Hypergraph(_tempdict)


def get_number_of_nbrs(H, u):
    """
        Returns the number of neighbours of u in hypergraph H
        Parameters
        ----------
        H: Hypernetx Hypergraph
        u: a vertex label

        Returns
        -------
        Integer
            The number of neighbours of u in H
    """
    nbrs = H.neighbors(u)
    if nbrs is None:  # u is not in H
        return 0
    return len(nbrs)


def get_degree(H, u):
    degree = 0
    try:
        degree = H.degree(u)
    except Exception as e:
        # print(e)
        pass
    
    return degree

def get_nbrs(H, u):
    """
        Returns the neighbours of u in hypergraph H
        Parameters
        ----------
        H: Hypernetx Hypergraph
        u: a vertex label

        Returns
        -------
        List
            The neighbours of u in H. [] if u is not in H.
    """
    nbrs = H.neighbors(u)
    if nbrs is None:  # u is not in H
        return []
    return nbrs


def get_hg(dataset):
    H = None
    if(dataset == "default"):
        dic = {
            0: ('FN', 'TH'),
            1: ('TH', 'JV'),
            2: ('BM', 'FN', 'JA'),
            3: ('JV', 'JU', 'CH', 'BM'),
            4: ('JU', 'CH', 'BR', 'CN', 'CC', 'JV', 'BM'),
            5: ('TH', 'GP'),
            6: ('GP', 'MP'),
            7: ('MA', 'GP')
        }

        H = hnx.Hypergraph(dic)

    elif(dataset in ['enron', "syn", "bin_1", "bin_2", "bin_4", "bin_5", "congress", "contact"]):

        # file location
        dataset_to_filename = {
            # real
            "enron" : "data/datasets/real/Enron.hyp",
            "congress" : "data/datasets/real/congress-bills.hyp",
            "contact" : "data/datasets/real/contact-primary-school.hyp",
            
            # synthetic
            "syn" : "data/datasets/synthetic/syn.hyp",
            "bin_1" : "data/datasets/synthetic/binomial_5_100_4_0.200000_sample_1_iter_1.txt",
            "bin_2" : "data/datasets/synthetic/binomial_5_500_4_0.200000_sample_2_iter_1.txt",
            "bin_4" : "data/datasets/synthetic/binomial_5_100_3_0.200000_sample_4_iter_1.txt",
            "bin_5" : "data/datasets/synthetic/binomial_5_500_3_0.200000_sample_5_iter_1.txt",

        }

        
        # split by
        dataset_to_split = {
            "enron" : " ",
            "congress" : ",",
            "contact" : ",",
     
            "syn" : ",",
            "bin_1" : ",",
            "bin_2" : ",",
            "bin_4" : ",",
            "bin_5" : ",",

        }

        
        dic = {}
        # read from file
        with open(dataset_to_filename[dataset]) as f:
            lines = f.readlines()

            for idx, line in enumerate(lines):
                edge = tuple(line[:-1].split(dataset_to_split[dataset]))
                dic[idx] = edge

        H = hnx.Hypergraph(dic)

    else:
        raise RuntimeError(dataset + " is not defined or implemented yet")


    return H

def get_N(H):
    """ Return num of vertices """
    return len(H.nodes)

def get_M(H):
    """ Return num of edges """
    return len(H.edges)

def get_degree_sequence(H):
    """ Return the degree sequence in descending order """
    assert isinstance(H, hnx.Hypergraph)
    degs = []
    for v in H.nodes:
        degs.append(H.degree(v))
    return sorted(degs,reverse = True)

def get_degree_distr(H):
    """ Return the degree distribution """
    assert isinstance(H, hnx.Hypergraph)
    degs = {}
    N = get_N(H)
    for v in H.nodes:
        d = H.degree(v)
        degs[d] = degs.get(d,0)+ (1.0/N)
    return sorted(degs.items(),reverse = True)

def get_dim_sequence(H):
    """ Return the dimension sequence in descending order """
    assert isinstance(H, hnx.Hypergraph)
    dims = []
    for e in H.edges:
        dims.append(H.dim(e)+1)
    return sorted(dims,reverse = True)

def get_dim_distr(H):
    """ Return the dimension distribution """
    assert isinstance(H, hnx.Hypergraph)
    dims = {}
    M = get_M(H)
    for _dim in get_dim_sequence(H):
        dims[_dim] = dims.get(_dim,0)+ (1.0/M)
    return sorted(dims.items(),reverse = True)

def get_nbr_sequence(H):
    """ Return the sequence nbrhood sizes  in descending order """
    assert isinstance(H, hnx.Hypergraph)
    nbrs = []
    for v in H.nodes:
        nbrs.append(get_number_of_nbrs(H,v))
    return sorted(nbrs,reverse = True)

def get_nbr_distr(H):
    """ Return the distribution of nbr sizes  """
    assert isinstance(H, hnx.Hypergraph)
    nbrs = {}
    N = get_N(H)
    for nbr in get_nbr_sequence(H):
        nbrs[nbr] = nbrs.get(nbr,0) + (1.0/N)
    return sorted(nbrs,reverse = True)

def get_degree_stats(H):
    """ Return the stats of degrees. """
    assert isinstance(H, hnx.Hypergraph)
    deg_seq = get_degree_sequence(H)
    stat = {'mean': None, 'max': None, 'min': None, '25%': None, '50%': None, '75%': None, 'std': None}
    _temp = pd.Series(deg_seq).describe()
    stat['mean'] = _temp['mean']
    stat['std'] = _temp['std']
    stat['min'] = _temp['min']
    stat['max'] = _temp['max']
    stat['25%'] = _temp['25%']
    stat['50%'] = _temp['50%']
    stat['75%'] = _temp['75%']
    return stat

def get_dim_stats(H):
    """ Return the stats of dimensions. """
    assert isinstance(H, hnx.Hypergraph)
    dim_seq = get_dim_sequence(H)
    stat = {'mean': None, 'max': None, 'min': None, '25%': None, '50%': None, '75%': None, 'std': None}
    _temp = pd.Series(dim_seq).describe()
    stat['mean'] = _temp['mean']
    stat['std'] = _temp['std']
    stat['min'] = _temp['min']
    stat['max'] = _temp['max']
    stat['25%'] = _temp['25%']
    stat['50%'] = _temp['50%']
    stat['75%'] = _temp['75%']
    return stat

def get_nbr_stats(H):
    """ Return the stats of neighbourhoods. """
    assert isinstance(H, hnx.Hypergraph)
    nbr_seq = get_nbr_sequence(H)
    stat = {'mean': None, 'max': None, 'min': None, '25%': None, '50%': None, '75%': None, 'std': None}
    _temp = pd.Series(nbr_seq).describe()
    stat['mean'] = _temp['mean']
    stat['std'] = _temp['std']
    stat['min'] = _temp['min']
    stat['max'] = _temp['max']
    stat['25%'] = _temp['25%']
    stat['50%'] = _temp['50%']
    stat['75%'] = _temp['75%']
    return stat

