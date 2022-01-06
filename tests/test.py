import sys
from hgDecompose.Hypergraph import Hypergraph
sys.path.append("../")
from hgDecompose.optimizedhgDecompose import HGDecompose
from hgDecompose.IncidenceRep import HypergraphL
from hgDecompose.utils import get_hg,get_localhg
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
parser.add_argument("--paramrand", "--parametric_randomtest", help="Number of Random Hypergraph to test", default=0, type=int)

args = parser.parse_args()
print(args.paramrand)
if (args.paramrand>0):
    from hgDecompose.utils import get_random_hg
    import random
    N = int(args.paramrand) # Number of random tests to conduct per parameter.
    
    if args.paramrand == 1:
        # parameter = {'n': 3, 'm': 2, 'card_max': 2}
        # parameter = {'n': 5, 'm': 3, 'card_max': 3}
        # parameter = {'n': 4, 'm': 3, 'card_max': 2}
        parameter = {'n': 5, 'm': 3, 'card_max': 3}

        m = parameter['m']
        n = parameter['n']
        card_max = parameter['card_max']
        # seed = 928051
        # seed = 711062
        # seed = 146683
        # seed = random.randint(0, 1000000)
        # seed = i
        seed = 695987
        print(parameter)
        print(' seed: ',seed)
        Hg = get_random_hg(n = n, m = m, edge_size_ub = card_max, seed = seed)
        print(Hg)
        Hg_cpy = deepcopy(Hg) 

        # hgDecompose = HGDecompose()
        # hgDecompose.improved2NBR(Hg, verbose=args.verbose)
        # core_compared = hgDecompose.core
        hgDecompose = HGDecompose()
        hgDecompose.bipartitedist2core(Hg, verbose=args.verbose)
        core_compared = hgDecompose.core

        if not args.verbose:
            hgDecompose = HGDecompose()
            hgDecompose.naiveNBR(Hg_cpy, verbose=args.verbose)
            core_base = hgDecompose.core

            print('Expected: ', core_base)
            print('Found: ', core_compared)
            # if (len(core_base) != len(core_compared)):
            #     print(Hg)
            # assert len(core_base) == len(core_compared), "Two returned cores do not have same length: " + str(len(core_base)) + " != " + str(len(core_compared))
            for v in core_base:
                assert v in core_compared, str(v) + " is not in core_compared"
                if (core_base[v] != core_compared[v]):
                    print(Hg)
                assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])

            # core_compared contains in core_base
            for v in core_compared:
                assert v in core_base, str(v) + " is not in core_base"
                assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])

            print("\nAll tests passed")

    else:
        param_list = [] 
        for n in range(5,6):
            for m in range(3, 5):
                for card_max in range(3,n):
                    param_list.append(
                        {'n': n, 'm': m, 'card_max' : card_max}
                    )
        # print(param_list)
        for parameter in param_list:
            m = parameter['m']
            n = parameter['n']
            card_max = parameter['card_max']
            for i  in range(0, N):
                # seed = 928051
                seed = random.randint(0, 1000000)
                # seed = i
                print(parameter)
                print(i,' seed: ',seed)
                Hg = get_random_hg(n = n, m = m, edge_size_ub = card_max, seed = seed)
                # print(Hg)
                Hg_cpy = deepcopy(Hg) 

                # hgDecompose = HGDecompose()
                # hgDecompose.improved2NBR(Hg, verbose=args.verbose)
                # core_compared = hgDecompose.core
                hgDecompose = HGDecompose()
                hgDecompose.bipartitedist2core(Hg, verbose=args.verbose)
                core_compared = hgDecompose.core

                hgDecompose = HGDecompose()
                hgDecompose.naiveNBR(Hg_cpy, verbose=args.verbose)
                core_base = hgDecompose.core

                # print(core_base)
                # print(core_compared)
                if (len(core_base) != len(core_compared)):
                    print(Hg)
                assert len(core_base) == len(core_compared), "Two returned cores do not have same length: " + str(len(core_base)) + " != " + str(len(core_compared))
                for v in core_base:
                    assert v in core_compared, str(v) + " is not in core_compared"
                    if (core_base[v] != core_compared[v]):
                        print(Hg)
                    assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])

                # core_compared contains in core_base
                for v in core_compared:
                    assert v in core_base, str(v) + " is not in core_base"
                    assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])

                print("\nAll tests passed")
    sys.exit(0)

if (args.rand>0):
    """ 
    Here we want to generate a large number of 
    small-sized random hypergraph and test correctness on those hypergraphs
    => Good for generating illustrative example for paper in order to make a point.
    => In this implementation, we are finding a random hypergraph to illustrate when and why Local core-correction matters. 
    """
    from hgDecompose.utils import get_random_hg
    import random
    N = int(args.rand)
    for i  in range(0, N):
        # seed = 544621
        seed = random.randint(0, 1000000)
        print(i,' seed: ',seed)
        Hg = get_random_hg(n = 5, m = 3, edge_size_ub = 3, seed = seed)
        # Hg_cpy = deepcopy(Hg)
        # print([e for e in Hg.edge_iterator()])
        hgDecompose = HGDecompose()
        hgDecompose.wrong_local_core(Hg, verbose=args.verbose)
        core_compared = hgDecompose.core

        # hgDecompose = HGDecompose()
        # hgDecompose.naiveNBR(Hg_cpy, verbose=args.verbose)
        # core_base = hgDecompose.core
        # hgDecompose.improvedNBR_simplified(Hg, verbose=args.verbose)
        # core_compared = deepcopy(hgDecompose.core)
        # hgDecompose.core = {}
        
        _d = {}
        for _id, e in Hg.edge_eid_iterator():
            _d[_id] = e 
        Hg_cpy = HypergraphL(_d)
        hgDecompose.opt_local_core(Hg_cpy, verbose=args.verbose)
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
if args.algo.startswith('opt') and 'local' in args.algo:
    H = get_localhg(args.dataset)
else:
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
    # scenes = {
    #     1: ('b', 'd'),
    #     2: ('d', 'a', 'h'),
    #     3: ('h', 'c', 'e', 'g')
    # }
    # H = Hypergraph(scenes)
    # Hg_cpy = Hypergraph(scenes)
    # hgDecompose = HGDecompose()
    hgDecompose.improved2NBR(H, s=args.param_s, verbose=args.verbose)
    # print(hgDecompose.core)
    # core_compared = hgDecompose.core
    # hgDecompose = HGDecompose()
    # hgDecompose.naiveNBR(Hg_cpy, verbose=args.verbose)
    # core_base = hgDecompose.core
    # for v in core_base:
    #     assert v in core_compared, str(v) + " is not in core_compared"
    #     assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])
    
    # for v in core_compared:
    #     assert v in core_base, str(v) + " is not in core_base"
    #     assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])

    # exit(1)

elif (args.algo == 'par_improved2_nbr'):
    assert args.param_s > 0 # Is this assertion valid?
    hgDecompose.parallel_improved2NBR(H, s=args.param_s, num_threads = args.nthreads, verbose=args.verbose)

elif (args.algo == 'par_improved3_nbr'):
    assert args.param_s > 0 # Is this assertion valid?
    hgDecompose.parallel_improved3NBR(H, s=args.param_s, num_threads = args.nthreads, verbose=args.verbose)

# elif(args.algo == "local_core"):
#     hgDecompose.local_core(H, verbose=args.verbose)

elif(args.algo == "recursive_local_core"):
    hgDecompose.local_core(H, verbose=args.verbose)

elif(args.algo == "iterative_local_core"):
    hgDecompose.iterative_local_core(H, verbose=args.verbose)

elif(args.algo == "bst_local_core"):
    hgDecompose.bst_local_core(H, verbose=args.verbose)

elif(args.algo == "improved_local_core"):
    hgDecompose.improved_local_core(H, verbose=args.verbose)
    # hgDecompose.improved_local_core_rev(H, verbose=args.verbose)

elif(args.algo == "opt_local_core"):
    hgDecompose.opt_local_core(H, verbose=args.verbose)

# elif(args.algo == "improved_local_core_bst"):
#     hgDecompose.improved_local_core(H, verbose=args.verbose, bst = True)

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