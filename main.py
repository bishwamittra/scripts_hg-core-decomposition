import sys
sys.path.append("HyperNetX")
import matplotlib.pyplot as plt
import networkx as nx
import hypernetx as hnx


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
bucket = {}

for node in nodes:
    print(node, list(H.neighbors(node)))