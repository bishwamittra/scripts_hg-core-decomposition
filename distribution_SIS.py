
import os
import argparse
import numpy as np
parser = argparse.ArgumentParser()
parser.add_argument("--thread", help="index of thread", default=-1, type=int)
parser.add_argument("--max_thread", help="maximum number of thread", default=1, type=int)
args = parser.parse_args()

algo_list = ['naive_nbr']
dataset_list = ['bin_1', 'bin_2', 'bin_4', 'bin_5', 'enron',  'contact', 'congress']

# all combination of experiments
configurations = []
for dataset in dataset_list:
    for algo in algo_list:
        if(algo in ['improved2_nbr','par_improved2_nbr','par_improved3_nbr']): # Additional param    
            delta = param_s_distinctvals[dataset]//num_divisions
            
            for s in range(1,param_s_distinctvals[dataset]+1, max(delta,1)):   
                if algo in ['par_improved2_nbr','par_improved3_nbr']:
                    for nthread in n_thread_list:
                        configurations.append((algo,dataset,s, nthread))
                configurations.append((algo, dataset, s, 4))
        else:
            if (algo in ['par_local_core']):
                for nthread in n_thread_list:
                    configurations.append((algo,dataset, 0, nthread))
            else:
                configurations.append((algo, dataset, 0, 4))


# print(len(configurations))
# distributing among threads
for i, configuration in enumerate(configurations):
    algo, dataset, s, nthreads = configuration
    if(i%args.max_thread == args.thread or args.thread == -1):
        cmd = "python -W ignore -u run.py" + \
              " --algo " + algo + \
              " --dataset " + dataset + \
              " --iterations " + str(iterations) + \
              " --param_s " + str(s) +\
              " --nthreads " + str(nthreads)
        print(cmd) 
        os.system(cmd) 

# TO DO: ignore assertion -O