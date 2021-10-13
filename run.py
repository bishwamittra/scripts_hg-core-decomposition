# import sys
# sys.path.append("HyperNetX")
# import matplotlib.pyplot as plt
# import networkx as nx
# import hypernetx as hnx
# from hgDecompose.hgDecompose import HGDecompose
# from hgDecompose.utils import get_hg_hnx
# from hgDecompose.newhgDecompose import HGDecompose
from hgDecompose.optimizedhgDecompose import HGDecompose
from hgDecompose.utils import get_hg, memory_usage_psutil
from hgDecompose.influence_propagation import propagate_for_all_vertices
import argparse
import pandas as pd
import pickle
import os
from copy import deepcopy

# arguments
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--thread", help="index of thread", default=-1, type=int)
parser.add_argument("-d", "--dataset", type=str, default="default")
parser.add_argument("-a", "--algo", type=str, default="naive_nbr")
parser.add_argument("-v", "--verbose", action='store_true')
parser.add_argument("-s", "--param_s", help="parameter for improve2_nbr", default=1, type=int)
parser.add_argument("--iterations", help="number of iterations", default=1, type=int)
parser.add_argument("-nt", "--nthreads", help="number of threads for improve3_nbr", default=4, type=int)
parser.add_argument("--sir", action='store_true')
parser.add_argument("-p", "--prob", help="parameter for Probability", default= 0.5, type=float)

args = parser.parse_args()


# Pandemic propagation
if(args.sir):

    input_H = get_hg(args.dataset)

    H = deepcopy(input_H)
    assert H is not None

    # Loading/saving to file
    os.system("mkdir -p tests/tmp")
    fname = "tests/tmp/" + args.dataset + "_" + args.algo + ".pkl"
    if(not os.path.isfile(fname)):
        hgDecompose = HGDecompose()
        if(args.algo == "naive_nbr"):
            hgDecompose.naiveNBR(input_H, verbose=args.verbose)
        elif(args.algo == "naive_degree"):
            hgDecompose.naiveDeg(input_H, verbose=args.verbose)
        else:

            raise RuntimeError(args.algo + " is not defined or implemented yet")

        core_base = hgDecompose.core
        # print(core_base)

        # dump file
        with open(fname, 'wb') as handle:
            pickle.dump(hgDecompose, handle, protocol= 4)


    else:
        # print("Retrieving saved file")
        with open(fname, 'rb') as handle:
            hgDecompose = pickle.load(handle)
            core_base = hgDecompose.core
    
    # print(core_base)
    entry = {}
    entry['dataset'] = args.dataset
    entry['p'] = float(args.prob)
    entry['algo'] = args.algo
    entry['result'] = propagate_for_all_vertices(H, core_base, p = float(args.prob), verbose=args.verbose)

    result = pd.DataFrame()
    result = result.append(entry, ignore_index=True)
    if(args.verbose): 
        print(entry)
        print("\n")
        print(", ".join(["\'" + column + "\'" for column in result.columns.tolist()]))

    os.system("mkdir -p data/output")
    result.to_csv('data/output/propagation_result.csv', header=False,
                            index=False, mode='a')



    quit()

# hyper-graph construction
# H = get_hg_hnx(args.dataset)
input_H = get_hg(args.dataset)
print("HG construction done!")
assert input_H is not None





for iteration in range(args.iterations):
    H = deepcopy(input_H)
    entry = {}
    entry['algo'] = args.algo
    entry['dataset'] = args.dataset
    entry['num_threads'] = args.nthreads
    # run algo
    hgDecompose = HGDecompose()
    if(args.algo == "naive_nbr"):
        hgDecompose.naiveNBR(H, verbose=args.verbose)

    elif(args.algo == "improved_nbr"):
        hgDecompose.improvedNBR(H, verbose=args.verbose)

    elif(args.algo == "improved_nbr_simple"):
        hgDecompose.improvedNBR_simplified(H, verbose=args.verbose)
        
    elif(args.algo == "naive_degree"):
        hgDecompose.naiveDeg(H, verbose=args.verbose)


    elif(args.algo == "improved2_nbr"):
        assert args.param_s > 0 # Is this assertion valid?
        hgDecompose.improved2NBR(H, s=args.param_s, verbose=args.verbose)

    elif (args.algo == 'par_improved2_nbr'):
        assert args.param_s > 0 # Is this assertion valid?
        hgDecompose.parallel_improved2NBR(H, s=args.param_s, num_threads = args.nthreads, verbose=args.verbose)
    
    elif (args.algo == 'par_improved3_nbr'):
        assert args.param_s > 0 # Is this assertion valid?
        hgDecompose.parallel_improved3NBR(H, s=args.param_s, num_threads = args.nthreads, verbose=args.verbose)
    
    elif(args.algo == "local_core"):
        hgDecompose.local_core(H, verbose=args.verbose)

    elif(args.algo == "par_local_core"):
        hgDecompose.par_local_core(H, verbose=args.verbose)

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
    entry['init time'] = hgDecompose.init_time
    entry['outerloop time'] = hgDecompose.loop_time
    entry['total iteration'] = hgDecompose.total_iteration
    entry['inner iteration'] = hgDecompose.inner_iteration
    entry['core_correction time'] = hgDecompose.core_correct_time
    if(True):
        entry['memory taken'] = memory_usage_psutil()
    # print(entry)
    result = pd.DataFrame()
    result = result.append(entry, ignore_index=True)
    # print('result: ',result['num subgraph call'].values[0],',',result['subgraph computation time'].values[0])
    # print('tolist(): ',result.columns.tolist())
    if(args.verbose and iteration==0): 
        print(entry)
        print("\n")
        print(", ".join(["\'" + column + "\'" for column in result.columns.tolist()]))

    os.system("mkdir -p data/output")
    result.to_csv('data/output/result.csv', header=False,
                            index=False, mode='a')



    # print(memory_usage_psutil())
    # print(memory_usage_psutil())