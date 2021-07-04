import sys
sys.path.append("HyperNetX")
import hypernetx as hnx
from hgDecompose.hgDecompose import HGDecompose

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
hgDecompose = HGDecompose()
hgDecompose.naiveDeg(H, verbose=False)
print(hgDecompose.core)
