class Hypergraph:
    def __init__(self, _edgedict=None):
        self.Incident = {}  # key => node, value = List of incident hyperedge/sets.
        self.nbr = {}  # key: node, value = List of Neighbours.
    
    def 