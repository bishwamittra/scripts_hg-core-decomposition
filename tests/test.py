import sys
sys.path.append("../")
from hgDecompose.optimizedhgDecompose import HGDecompose
from hgDecompose.utils import get_hg
import argparse
import pandas as pd
import os
os.system("mkdir -p tests/tmp")
from copy import deepcopy
import pickle

# arguments
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--thread", help="index of thread", default=-1, type=int)
parser.add_argument("-d", "--dataset", type=str, default="default")
parser.add_argument("-ab", "--algo_base", type=str, default="naive_nbr")
parser.add_argument("-a", "--algo", type=str, default="naive_nbr")
parser.add_argument("-v", "--verbose", action='store_true')
parser.add_argument("-s", "--param_s", help="parameter for improve2_nbr", default=1, type=int)
parser.add_argument("-nt", "--nthreads", help="number of threads for improve3_nbr", default=4, type=int)
parser.add_argument("--rand", "--randomtest", help="Number of Random Hypergraph to test", default=0, type=int)

args = parser.parse_args()

if (args.rand>0):
    """ 
    Here we want to generate a large number of 
    small-sized random hypergraph and test correctness on those hypergraphs
    => Good for generating illustrative example for paper in order to make a point.
    """
    from hgDecompose.utils import get_random_hg
    import random
    N = int(args.rand)
    for i  in range(0, N):
        # seed = 544621
        seed = random.randint(0, 1000000)
        print(i,' seed: ',seed)
        Hg = get_random_hg(n = 5, m = 3, edge_size_ub = 3, seed = seed)
        Hg_cpy = deepcopy(Hg)
        print([e for e in Hg.edge_iterator()])
        # hgDecompose = HGDecompose()
        # hgDecompose.wrong_local_core(Hg, verbose=args.verbose)
        # core_compared = hgDecompose.core

        hgDecompose = HGDecompose()
        hgDecompose.improvedNBR_simplified(Hg, verbose=args.verbose)
        core_compared = deepcopy(hgDecompose.core)
        hgDecompose.core = {}
        
        hgDecompose.naiveNBR(Hg_cpy, verbose=args.verbose)
        core_base = hgDecompose.core
        
        # print(core_base)
        # print(core_compared)
        for v in core_base:
            assert v in core_compared, str(v) + " is not in core_compared"
            assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])

        # core_compared contains in core_base
        for v in core_compared:
            assert v in core_base, str(v) + " is not in core_base"
            assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])

        print("\nAll tests passed")
    sys.exit(0)

# hyper-graph construction
# H = get_hg_hnx(args.dataset)
# input_H = get_hg(args.dataset)
print("HG construction done!")
# assert input_H is not None

# Forced values
fname = "tests/tmp/" + args.dataset + ".pkl"
if(not os.path.isfile(fname)):
    H = get_hg(args.dataset)
    assert H is not None
    hgDecompose = HGDecompose()
    if(args.algo_base == "naive_nbr"):
        hgDecompose.naiveNBR(H, verbose=args.verbose)
    else:

        raise RuntimeError(args.algo_base + " is not defined or implemented yet")

    core_base = hgDecompose.core

    # dump file
    with open(fname, 'wb') as handle:
        pickle.dump(hgDecompose, handle, protocol= 4)


else:
    # print("Retrieving saved file")
    with open(fname, 'rb') as handle:
        hgDecompose = pickle.load(handle)
        core_base = hgDecompose.core


# compared algo
# H = deepcopy(input_H)
H = get_hg(args.dataset)
assert H is not None
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

# elif(args.algo == "local_core"):
#     hgDecompose.local_core(H, verbose=args.verbose)

elif(args.algo == "local_core"):
    hgDecompose.local_core(H, verbose=args.verbose, bst = False)

elif(args.algo == "bst_local_core"):
    hgDecompose.local_core(H, verbose=args.verbose, bst = True)

elif(args.algo == "wlocal_core"):
    hgDecompose.wrong_local_core(H, verbose=args.verbose)

elif(args.algo == "par_local_core"):
    hgDecompose.par_local_core(H, verbose=args.verbose)

else:
    raise RuntimeError(args.algo + " is not defined or implemented yet")

core_compared = hgDecompose.core


# assertions
# len
assert len(core_base) == len(core_compared), "Two returned cores do not have same length: " + str(len(core_base)) + " != " + str(len(core_compared))

# print all discrepencies
# for v in core_base:
#     if (v not in core_compared):
#         print(str(v) + " is not in core_compared")
#     if (core_base[v] != core_compared[v]):
#         print(str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v]))

# k = 24
# from tests.verify_kcore import verify_subgraph
# verify_subgraph(H,threshold= k, cores = core_compared)

for v in core_base:
    assert v in core_compared, str(v) + " is not in core_compared"
    assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])

# core_compared contains in core_base
for v in core_compared:
    assert v in core_base, str(v) + " is not in core_base"
    assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])

print("\nAll tests passed")