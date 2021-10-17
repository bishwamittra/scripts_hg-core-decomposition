import math
class HypergraphL:
    def __init__(self, _edgedict=None):
        self.inc_dict = {}  # key => node, value = List of incident hyperedge ids.
        self.e_id_to_edge = {} # key => hyperedge_id, value => List of vertices in a hyperedge
        self.init_nbr = {}  # key: node, value = List of Neighbours.
        self.init_nbrsize = {} # initial nbrhood sizes. 
        self.init_nodes = []

        for e_id, e in _edgedict.items():
            self.e_id_to_edge[e_id] = e 
            for v in e:
                if v not in self.inc_dict:
                    self.inc_dict[v] = []
                    self.init_nodes.append(v)
                self.inc_dict[v].append(e_id)
                nbr_v = self.init_nbr.get(v, set()).union(e)
                nbr_v.remove(v)
                self.init_nbrsize[v] = len(nbr_v)
                self.init_nbr[v] = nbr_v  # neighbourbood set update
        
        self.edge_min_hindex = {} # key = edge_id, value => min (h_index of vertices in hyperedge edge_id)
        for v in self.init_nodes:
            nbr_v = self.init_nbrsize[v]
            for e_id in self.inc_dict[v]:
                val = self.edge_min_hindex.get(e_id, math.inf)
                self.edge_min_hindex[e_id] = min(nbr_v, val)

    def get_edge_byindex(self, e_id):
        return self.e_id_to_edge[e_id]
        
    def get_init_nbrlen(self, v):
        return self.init_nbrsize[v]

    def iterate_inc_min_hindices(self, v):
        for e_id in self.inc_edgeId_iterator(v):
            yield self.get_min_hindex[e_id]

    def get_min_hindex(self, e_id):
        return self.edge_min_hindex[e_id]

    def update_min_hindex(self, v, h_v):
        """ Given a new value of h_v, update h_min for its incident hyperedges, whenever appropriate """
        for e_id in self.inc_edgeId_iterator(v): 
            if self.get_min_hindex(e_id) > h_v:
                self.edge_min_hindex[e_id] = h_v

    def init_nbr_iterator(self, v):
        for u in self.init_nbr[v]:
            yield u 

    def inc_edge_iterator(self, v):
        for e_id in self.inc_dict[v]: 
            yield self.e_id_to_edge[e_id]
    
    def inc_edgeId_iterator(self, v):
        for e_id in self.inc_dict[v]: 
            yield e_id 

    def init_edge_iterator(self):
        for e_id in self.e_id_to_edge.keys():
            yield self.e_id_to_edge[e_id]

    def init_node_iterator(self):
        for v in self.init_nodes:
            yield v