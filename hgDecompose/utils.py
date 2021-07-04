import sys

sys.path.append("HyperNetX")
import hypernetx as hnx


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
