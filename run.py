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

# hyper-graph construction
H = None
if(args.dataset == "default"):
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

elif(args.dataset in ['enron', "syn"]):

    # file location
    dataset_to_filename = {
        "enron" : "data/real/Enron.hyp",
        "syn" : "data/synthetic/syn.hyp"
    }

    # split by
    dataset_to_split = {
        "enron" : " ", 
        "syn" : ","
    }

    
    dic = {}
    # read from file
    with open(dataset_to_filename[args.dataset]) as f:
        lines = f.readlines()

        for idx, line in enumerate(lines):
            edge = tuple(line[:-1].split(dataset_to_split[args.dataset]))
            dic[idx] = edge

    H = hnx.Hypergraph(dic)

else:
    raise RuntimeError(args.dataset + " is not defined or implemented yet")


assert H is not None


entry = {}
entry['algo'] = args.algo
entry['dataset'] = args.dataset

# run algo
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
    