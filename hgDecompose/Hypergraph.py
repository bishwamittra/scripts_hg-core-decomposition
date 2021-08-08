import copy 
import sys

sys.path.append("HyperNetX")
import hypernetx as hnx

class Hypergraph:
    """ 
    Our own hypergraph representation class. 
    We store hyperedge list in compressed format using two things- 1) e_indices (a dict) 2) e_nodes (a list)
    Although edge-centric queries (e.g. edge enumeration) are facilitated in this way, node-centric queries are not convenient.
    To support node-centric queries, we also maintain incidence dictionary inc_dict (key = v_ids, values = incident edge ids)
    """
    def __init__(self, _edgedict = None):
        if _edgedict is None: # Returns an empty Hypergraph
            return
        self.e_indices = {} # (position, edge_size) of edge e in e_nodes list
        self.e_nodes = [] # flattened edge list
        self.inc_dict = {}
        self.i = 0
        for e_id,e in _edgedict.items():
            _len = len(e)
            self.e_indices[e_id] = (self.i,self.i+_len)
            for v in e:
                self.e_nodes.append(v)
                self.inc_dict[v] = self.inc_dict.get(v,[]) + [e_id]
            self.i += _len

    def add_edge(self, e_id, e_nodes):
        """ Add an edge to the hypergraph. It does not check repeated edge."""
        _len = len(e_nodes)
        self.e_indices[e_id] = (self.i, self.i+_len)
        for v in e_nodes:
            self.e_nodes.append(v)
            self.inc_dict[v] = self.inc_dict.get(v,[]) + [e_id]
        self.i += _len

    def get_edge_byindex(self, e_id):
        """ Return edge by edge_id """
        e_start, e_end = self.e_indices[e_id]
        return self.e_nodes[e_start:e_end]

    def edge_iterator(self):
        """ returns: iterator """
        for e_id in self.e_indices.keys():
            yield self.get_edge_byindex(e_id)

    def node_iterator(self):
        """ returns: iterator """
        for v_id in self.inc_dict.keys():
            yield v_id

    def nodes(self):
        """ returns: list of vertices """
        return [v for v in self.node_iterator()]

    def edges(self):
        """ returns: list of edges (each edge is a list of vertex ids) """
        return [ e for e in self.edge_iterator() ] 

    def neighbors(self, u):
        """ 
        input: u (vertex id)
        returns: set"""
        if u not in self.inc_dict.keys():
            return set() # Empty set
        nbrs = set()
        for e_id in self.inc_dict.get(u,[]):
            e = self.get_edge_byindex(e_id)
            for v in e:
                nbrs.add(v)
        nbrs.remove(u)
        return nbrs
        
    def get_number_of_nbrs(self, u):
        return len(self.neighbors(u))

    def degree(self, u):
        """ returns: integer """
        return len(self.inc_dict.get(u,[]))

    def dim(self, e):
        """ returns: integer """
        return len(e) - 1


    def strong_subgraph(self, vertex_list):
        """ returns: Hypergraph object. """
        H = Hypergraph()
        e_indices = {} # (position, edge_size) of edge e in e_nodes list
        e_nodes = [] # flattened edge list
        inc_dict = {}
        H.i = 0
        
        # print('inc_dict: ',self.inc_dict.items())
        # print('e_indices: ',self.e_indices.items())
        # print('e_nodes: ',self.e_nodes)
        
        for v in vertex_list:
            for e_id in self.inc_dict.get(v,[]):
                if e_id not in e_indices:
                    e_start, e_end = self.e_indices[e_id]
                    flag = True
                    e = self.e_nodes[e_start:e_end]
                    for u in e:
                        if u not in vertex_list:
                            flag = False
                            break
                    if flag:
                        e_nodes += e
                        _lene = (e_end - e_start)
                        e_indices[e_id] = (H.i, H.i+ _lene)
                        inc_dict[v] = inc_dict.get(v,[])+[e_id]
                        H.i+= _lene
                else:
                    inc_dict[v] = inc_dict.get(v,[])+[e_id]

        # print('After: ','inc_dict = ',inc_dict.items(),'\n','e_indices = ',e_indices,'\n',' e_nodes = ',e_nodes)
        H.e_nodes = e_nodes
        H.inc_dict = inc_dict
        H.e_indices = e_indices
        return H
    
    def strong_subgraph2(self, vertex_list):
        """ 
        Another implementation of strong_subgraph
        returns: Hypergraph object. 
        """
        H = Hypergraph()
        e_indices = {} # (position, edge_size) of edge e in e_nodes list
        e_nodes = [] # flattened edge list
        inc_dict = {}
        H.i = 0
        
        # print('inc_dict: ',self.inc_dict.items())
        # print('e_indices: ',self.e_indices.items())
        # print('e_nodes: ',self.e_nodes)
        
        # for v in vertex_list:
        #     for e_id in self.inc_dict.get(v,[]):
        #         if e_id not in e_indices:
        #             e_start, e_end = self.e_indices[e_id]
        #             flag = True
        #             e = self.e_nodes[e_start:e_end]
        #             for u in e:
        #                 if u not in vertex_list:
        #                     flag = False
        #                     break
        #             if flag:
        #                 e_nodes += e
        #                 _lene = (e_end - e_start)
        #                 e_indices[e_id] = (H.i, H.i+ _lene)
        #                 inc_dict[v] = inc_dict.get(v,[])+[e_id]
        #                 H.i+= _lene
        #         else:
        #             inc_dict[v] = inc_dict.get(v,[])+[e_id]

        for e_id in self.e_indices:
            flag = True
            e = self.get_edge_byindex(e_id)
            for u in e:
                if u not in vertex_list:
                    flag = False
                    break
            if flag:
                e_start, e_end = self.e_indices[e_id]
                e_nodes += e 
                _lene = (e_end - e_start)
                e_indices[e_id] = (H.i, H.i+ _lene)
                H.i+= _lene

        for e_id in e_indices:
            e = self.get_edge_byindex(e_id)
            for u in e:
                inc_dict[u] = inc_dict.get(u,[]) + [e_id]

        # print('After: ','inc_dict = ',inc_dict.items(),'\n','e_indices = ',e_indices,'\n',' e_nodes = ',e_nodes)
        H.e_nodes = e_nodes
        H.inc_dict = inc_dict
        H.e_indices = e_indices
        return H

    def get_hnx_format(self):
        _tempH = {}
        for e_id in self.e_indices.keys():
            _tempH[e_id] = self.get_edge_byindex(e_id)
        return hnx.Hypergraph(_tempH)


    # def weak_subgraph(self, vertex_list):
    #     """ returns: Hypergraph object. """
    #     pass 