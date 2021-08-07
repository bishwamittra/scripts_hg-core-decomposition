import sys
sys.path.append("HyperNetX")
import matplotlib.pyplot as plt
import networkx as nx
import hypernetx as hnx
from hgDecompose.hgDecompose import HGDecompose
from hgDecompose.utils import get_hg
import argparse
import pandas as pd
import os

# arguments
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--thread", help="index of thread", default=-1, type=int)
parser.add_argument("-d", "--dataset", type=str, default="default")
parser.add_argument("-a", "--algo", type=str, default="naive_nbr")
parser.add_argument("-v", "--verbose", action='store_true')
parser.add_argument("-s", "--param_s", help="parameter for improve2_nbr", default=1, type=int)
parser.add_argument("--iterations", help="number of iterations", default=1, type=int)



args = parser.parse_args()

# hyper-graph construction
H = get_hg(args.dataset)
print("HG construction done!")
assert H is not None


for iteration in range(args.iterations):
    entry = {}
    entry['algo'] = args.algo
    entry['dataset'] = args.dataset

    # run algo
    hgDecompose = HGDecompose()
    if(args.algo == "naive_nbr"):
        hgDecompose.naiveNBR(H, verbose=args.verbose)

    elif(args.algo == "improved_nbr"):
        hgDecompose.improvedNBR(H, verbose=args.verbose)
        
    elif(args.algo == "naive_degree"):
        hgDecompose.naiveDeg(H, verbose=args.verbose)


    elif(args.algo == "improved2_nbr"):
        assert args.param_s > 0 # Is this assertion valid?
        hgDecompose.improved2NBR(H, s=args.param_s, verbose=args.verbose)

    else:
        raise RuntimeError(args.algo + " is not defined or implemented yet")


    entry['core'] = hgDecompose.core
    entry['param_s'] = args.param_s
    entry['execution time'] = hgDecompose.execution_time
    entry['bucket update time'] = hgDecompose.bucket_update_time
    entry['neighborhood call time'] = hgDecompose.neighborhood_call_time
    entry['degree call time'] = hgDecompose.degree_call_time
    entry['num bucket update'] = hgDecompose.num_bucket_update
    entry['num neighborhood computation'] = hgDecompose.num_neighborhood_computation
    entry['num degree computation'] = hgDecompose.num_degree_computation
    entry['subgraph computation time'] = hgDecompose.subgraph_time
    entry['num subgraph call'] = hgDecompose.num_subgraph_call

    result = pd.DataFrame()
    result = result.append(entry, ignore_index=True)

    if(args.verbose and iteration==0): 
        print(entry)
        print(", ".join(["\'" + column + "\'" for column in result.columns.tolist()]))

    os.system("mkdir -p data/output")
    result.to_csv('data/output/result.csv', header=False,
                            index=False, mode='a')
        