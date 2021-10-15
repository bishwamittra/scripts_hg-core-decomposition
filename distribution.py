
import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--thread", help="index of thread", default=-1, type=int)
parser.add_argument("--max_thread", help="maximum number of thread", default=1, type=int)
args = parser.parse_args()

# ['enron', 'congress', 'contact', 'syn', 'bin_1', 'bin_2', 'bin_4', 'bin_5']
# algo_list = ['naive_nbr', 'improved_nbr', 'improved2_nbr', 'naive_degree']
# algo_list = ['naive_nbr', 'improved_nbr']
algo_list = ['improved_nbr_simple']
# algo_list = ['bst_local_core']
# algo_list = ['par_local_core']
# algo_list = ['naive_nbr', 'improved_nbr','improved2_nbr','par_improved2_nbr']
# algo_list = ['par_improved2_nbr','par_improved3_nbr','naive_nbr', 'improved_nbr','improved2_nbr']
# algo_list = ['par_improved2_nbr','par_improved3_nbr','improved2_nbr']
# dataset_list = ['dblp','amazon']
# dataset_list = ['syn', 'bin_1', 'bin_2', 'bin_4', 'bin_5', 'enron', 'congress', 'contact', 'dblp','amazon']
dataset_list = ['bin_1', 'bin_2', 'bin_4', 'bin_5', 'enron',  'contact','congress','dblp']
n_thread_list = [1,2,4,8,16,32,64]
# param_s_dict = {
#                 'syn':(-1,3), 'bin_1':(25, 33), 'bin_2':(184, 193), 'bin_4':(19,24),
#                  'bin_5':(128, 140), 'enron': (-1, 40), 'congress': (1, 368), 'contact': (18, 47), 
#                  'dblp': (-1, 279), 'amazon': None
#                  }
param_s_distinctvals = {'syn': 3, 'bin_1': 6, 'bin_2': 8, 'bin_4': 4,
                 'bin_5':9, 'enron': 41, 'congress': 196, 'contact': 27, 
                 'dblp': 86, 'amazon': None
                 }
# param_s = [i+1 for i in range(10)]
iterations = 5
num_divisions = 10

# small exp
# iterations = 1
# dataset_list = ['default', 'syn']

# assert iterations > 1

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