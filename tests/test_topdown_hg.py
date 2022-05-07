import sys
from hgDecompose.Hypergraph import Hypergraph
from hgDecompose.optimizedhgDecompose import HGDecompose
sys.path.append("../")
from hgDecompose.optimizedGDecompose import HDecompose
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
        seed = 10012
        print(parameter)
        print(' seed: ',seed)
        Hg = get_random_hg(n = n, m = m, edge_size_ub = card_max, seed = seed)
        print(Hg)
        Hg_cpy = deepcopy(Hg) 
        hgDecompose = HDecompose()
        hgDecompose.top_down(Hg, s=args.param_s, verbose=True)
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
        for n in range(5,20):
            for m in range(3, n):
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

                hgDecompose = HDecompose()
                hgDecompose.top_down(Hg, s=args.param_s, verbose=False)
                core_compared = hgDecompose.core

                hgDecompose = HGDecompose()
                hgDecompose.naiveNBR(Hg_cpy, verbose=args.verbose) # Naive Peeling
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

# scenes = {
#     1: ('c', 'e'),
#     2: ('a', 'b'),
#     3: ('b', 'c'),
#     4: ('a', 'c'),
#     5: ('c', 'd'),
#     6: ('a','d')
# }
scenes = {
            0: ('E', 'D'),
            1: ('D', 'H'),
            2: ('G', 'E', 'F'),
            3: ('H', 'J', 'I', 'G'),
            4: ('J', 'I', 'M', 'L', 'K', 'H', 'G'),
            5: ('D', 'C'),
            6: ('C', 'B'),
            7: ('A', 'C')
}
# H = Hypergraph(scenes)
# Hg_cpy = Hypergraph(scenes)
# hgDecompose = HGDecompose()
# hgDecompose.improved2NBR(H, s=args.param_s, verbose=False)
# core_compared = hgDecompose.core
# print('Topdown: ',sorted(core_compared.items()))
""" For graph """
H = Hypergraph(scenes)
hgDecompose = HDecompose()
hgDecompose.top_down(H, s=args.param_s, verbose=True)
core_compared = hgDecompose.core
print('Topdown: ',sorted(core_compared.items()))

Hg_cpy = Hypergraph(scenes)
hgDecompose = HGDecompose()
hgDecompose.naiveNBR(Hg_cpy, verbose=args.verbose)
core_base = hgDecompose.core
print('Baseline: ',sorted(core_base.items()))
for v in core_base:
    assert v in core_compared, str(v) + " is not in core_compared"
    assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])

for v in core_compared:
    assert v in core_base, str(v) + " is not in core_base"
    assert core_base[v] == core_compared[v], str(v)+" :Output core is different in " + str(core_base[v]) + " & " + str(core_compared[v])
print('Correct')
exit(1)