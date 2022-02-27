# # import sys
# # sys.path.append("../")
# from hgDecompose.optimizedhgDecompose import HGDecompose
# from hgDecompose.utils import get_hg
# import argparse
# import pandas as pd
# import os
# os.system("mkdir -p tests/tmp")
# from copy import deepcopy
# import pickle

# # arguments
# parser = argparse.ArgumentParser()
# parser.add_argument("-t", "--thread", help="index of thread", default=-1, type=int)
# parser.add_argument("-d", "--dataset", type=str, default="default")
# parser.add_argument("-ab", "--algo_base", type=str, default="naive_nbr")
# parser.add_argument("-a", "--algo", type=str, default="naive_nbr")
# parser.add_argument("-v", "--verbose", action='store_true')
# parser.add_argument("-s", "--param_s", help="parameter for improve2_nbr", default=1, type=int)
# parser.add_argument("-nt", "--nthreads", help="number of threads for improve3_nbr", default=4, type=int)


# args = parser.parse_args()

# # hyper-graph construction
# # H = get_hg_hnx(args.dataset)
# # input_H = get_hg(args.dataset)
# print("HG construction done!")
# # assert input_H is not None

# # Forced values
# fname = "tests/tmp/" + args.dataset + ".pkl"
# if(not os.path.isfile(fname)):
#     H = get_hg(args.dataset)
#     assert H is not None
#     hgDecompose = HGDecompose()
#     if(args.algo_base == "naive_nbr"):
#         hgDecompose.naiveNBR(H, verbose=args.verbose)
#     else:

#         raise RuntimeError(args.algo_base + " is not defined or implemented yet")

#     core_base = hgDecompose.core

#     # dump file
#     with open(fname, 'wb') as handle:
#         pickle.dump(hgDecompose, handle, protocol= 4)


# else:
#     # print("Retrieving saved file")
#     with open(fname, 'rb') as handle:
#         hgDecompose = pickle.load(handle)
#         core_base = hgDecompose.core


# # compared algo
# # H = deepcopy(input_H)
# H = get_hg(args.dataset)
# assert H is not None
# hgDecompose = HGDecompose()
# if(args.algo == "naive_nbr"):
#     hgDecompose.naiveNBR(H, verbose=args.verbose)

# elif(args.algo == "improved_nbr"):
#     hgDecompose.improvedNBR(H, verbose=args.verbose)
    
# elif(args.algo == "naive_degree"):
#     hgDecompose.naiveDeg(H, verbose=args.verbose)


# elif(args.algo == "improved2_nbr"):
#     assert args.param_s > 0 # Is this assertion valid?
#     hgDecompose.improved2NBR(H, s=args.param_s, verbose=args.verbose)

# elif (args.algo == 'par_improved2_nbr'):
#     assert args.param_s > 0 # Is this assertion valid?
#     hgDecompose.parallel_improved2NBR(H, s=args.param_s, num_threads = args.nthreads, verbose=args.verbose)

# elif (args.algo == 'par_improved3_nbr'):
#     assert args.param_s > 0 # Is this assertion valid?
#     hgDecompose.parallel_improved3NBR(H, s=args.param_s, num_threads = args.nthreads, verbose=args.verbose)

# elif(args.algo == "par_local_core"):
#     hgDecompose.par_local_core(H, verbose=args.verbose)

# else:
#     raise RuntimeError(args.algo + " is not defined or implemented yet")

# core_compared = hgDecompose.core


# # assertions
# # len
# assert len(core_base) == len(core_compared), "Two returned cores do not have same length: " + str(len(core_base)) + " != " + str(len(core_compared))

# # core_base contains in core_compared
# for v in core_base:
#     assert v in core_compared, str(v) + " is not in core_compared"
#     assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])

# # core_compared contains in core_base
# for v in core_compared:
#     assert v in core_base, str(v) + " is not in core_base"
#     assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])

# print("\nAll tests passed")


import networkx as nx
from hgDecompose.optimizedhgDecompose import HGDecompose
from hgDecompose.utils import get_hg, memory_usage_psutil,get_localhg,check_connectivity
from hgDecompose.influence_propagation import propagate_for_all_vertices, propagate_for_random_seeds, run_intervention_exp2,run_intervention_exp2_explain
from hgDecompose.sis_propagation import propagateSIS_for_all_vertices
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
parser.add_argument("--sis", action='store_true')
parser.add_argument("--sir", action='store_true')
parser.add_argument("--sir_exp2", action='store_true')
parser.add_argument("--sir_exp3", action='store_true') # intervention
parser.add_argument("--sir_exp3_explanation", action = 'store_true')
parser.add_argument("--con", help="Is connected hypergraph", action='store_true')
parser.add_argument("-p", "--prob", help="parameter for Probability", default= 0.3, type=float)
parser.add_argument("-g", "--gamma", help="parameter for Probability", default= 0.01, type=float)

args = parser.parse_args()

if args.algo == 'opt_local_core':
    input_H = get_localhg(args.dataset)
else:
    input_H = get_hg(args.dataset)
print("HG construction done!")
assert input_H is not None

for iteration in range(args.iterations):
    H = deepcopy(input_H)
    entry = {}
    entry['algo'] = args.algo
    entry['dataset'] = args.dataset
    entry['num_threads'] = args.nthreads
    entry['init_nbr'] = H.init_nbr
    # run algo
    hgDecompose = HGDecompose()
    if(args.algo == "naive_nbr"):
        hgDecompose.naiveNBR(H, verbose=args.verbose)

    elif(args.algo == "improved_nbr_simple"):
        hgDecompose.improvedNBR_simplified(H, verbose=False)

    elif(args.algo == "opt_local_core"):
        # Run local_core algorithm while storing core-correction ammount and other auxiliary information.
        hgDecompose.opt_local_core(H, verbose=args.verbose, store_core_information=True, filename="data/output/"+args.dataset+"_local_core.csv", info_dic={'algo' : args.algo, 'dataset' : args.dataset, 'num_threads' : args.nthreads, 'outer iteration' : iteration})
        
        # Run local_core algorithm without storing other auxiliary information.
        # hgDecompose.opt_local_core(H, verbose=args.verbose, store_core_information=False)
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
    entry['h_index_time'] = hgDecompose.h_index_time
    entry['tau'] = hgDecompose.max_n  # For #iterations vs dataset barplot
    entry['core_correction_volume'] = hgDecompose.core_correctionvol_n #  core_corrections volume per iteration => Ammount of core_correction done. => Relation with runtime
    entry['sum_core_correction_volume'] = hgDecompose.core_correction_volume  # For core_correction volume vs dataset plot
    entry['reduction_in_hhat']  = hgDecompose.reduction_hhat_n  # [ hhat^{n-1} - hhat^{n}, for n \in [1, tau] ] => Convergence plot.

    if(True):
        entry['memory taken'] = memory_usage_psutil()
    # print(entry)
    result = pd.DataFrame()
    result = result.append(entry, ignore_index=True)
    # print('result: ',result['num subgraph call'].values[0],',',result['subgraph computation time'].values[0])
    # print('tolist(): ',result.columns.tolist())
    # print("iter: ",iteration)
    if(args.verbose and iteration==0): 
        # print(entry)
        print("\n")
        print(", ".join(["\'" + column + "\'" for column in result.columns.tolist()]))

    os.system("mkdir -p data/output")
    # print(result)
    result.to_csv('data/output/result_analysis.csv', header=False,
                            index=False, mode='a')
    # result.to_csv('data/output/result_temp.csv', header=False,
    #                         index=False, mode='a')
    # result.to_csv('data/output/result_protein.csv', header=False,
    #                         index=False, mode='a')
    # result.to_csv('data/output/result_gowalla.csv', header=False,
    #                         index=False, mode='a')
    print(", ".join(["\'" + column + "\'" for column in result.columns.tolist()]))