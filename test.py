# import sys
# sys.path.append("HyperNetX")
# import hypernetx as hnx
# from hgDecompose.hgDecompose import HGDecompose

# scenes = {
#     0: ('FN', 'TH'),
#     1: ('TH', 'JV'),
#     2: ('BM', 'FN', 'JA'),
#     3: ('JV', 'JU', 'CH', 'BM'),
#     4: ('JU', 'CH', 'BR', 'CN', 'CC', 'JV', 'BM'),
#     5: ('TH', 'GP'),
#     6: ('GP', 'MP'),
#     7: ('MA', 'GP')
# }

# H = hnx.Hypergraph(scenes)
# hgDecompose = HGDecompose()
# # hgDecompose.naiveDeg(H, verbose=False)
# hgDecompose.improvedNBR(H, verbose=True)
# # hgDecompose.improved2NBR(H, verbose=True)
# print(hgDecompose.core)


from multiprocessing import Pool
from time import time

def f(arg):
    x,y = arg
    return x*y, x*y

if __name__ == '__main__':
    start_time = time()
    with Pool(3) as p:
        print(p.map(f, [(1,1), (2,2), (3,5)]))
    print(time() - start_time)