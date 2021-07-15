import sys
sys.path.append("HyperNetX")
import matplotlib.pyplot as plt
import networkx as nx
import hypernetx as hnx
from hgDecompose.hgDecompose import HGDecompose
import argparse
import pandas as pd
import os

# arguments
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--thread", help="index of thread", default=-1, type=int)
parser.add_argument("-d", "--dataset", type=str, default="default")
parser.add_argument("-a", "--algo", type=str, default="naive_nbr")
parser.add_argument("-v", "--verbose", action='store_true')


args = parser.parse_args()

if(args.dataset == "default"):
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


entry = {}
entry['algo'] = args.algo
entry['dataset'] = args.dataset

hgDecompose = HGDecompose()

if(args.algo == "naive_nbr"):
    hgDecompose.naiveNBR(H, verbose=False)
    
elif(args.algo == "naive_degree"):
    hgDecompose.naiveDeg(H, verbose=False)

else:
    raise RuntimeError(args.algo + " is not defined or implemented yet")


entry['core'] = hgDecompose.core
entry['execution time'] = hgDecompose.execution_time
entry['bucket update time'] = hgDecompose.bucket_update_time
entry['neighborhood call time'] = hgDecompose.neighborhood_call_time
entry['degree call time'] = hgDecompose.degree_call_time
entry['num bucket update'] = hgDecompose.num_bucket_update
entry['num neighborhood computation'] = hgDecompose.num_neighborhood_computation
entry['num degree computation'] = hgDecompose.num_degree_computation

result = pd.DataFrame()
result = result.append(entry, ignore_index=True)

if(args.verbose): 
    print(", ".join(["\'" + column + "\'" for column in result.columns.tolist()]))

os.system("mkdir -p data/output")
result.to_csv('output/result.csv', header=False,
                        index=False, mode='a')
    