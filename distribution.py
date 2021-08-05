
import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--thread", help="index of thread", default=-1, type=int)
parser.add_argument("--max_thread", help="maximum number of thread", default=1, type=int)
args = parser.parse_args()

# ['enron', 'congress', 'contact', 'syn', 'bin_1', 'bin_2', 'bin_4', 'bin_5']
algo_list = ['naive_nbr', 'improved_nbr', 'improved2_nbr', 'naive_degree']
dataset_list = ['syn', 'bin_1', 'bin_2', 'bin_4', 'bin_5', 'enron', 'congress', 'contact']
param_s = [i+1 for i in range(10)]
iterations = 10

# small exp
# iterations = 1
# dataset_list = ['default', 'syn']

# assert iterations > 1

# all combination of experiments
configurations = []
for dataset in dataset_list:
    for algo in algo_list:
        if(algo in ['improved2_nbr']): # Additional param            
            for s in param_s:    
                configurations.append((algo, dataset, s))
        else:
            configurations.append((algo, dataset, 0))



# print(len(configurations))
# distributing among threads
for i, configuration in enumerate(configurations):
    algo, dataset, s = configuration
    if(i%args.max_thread == args.thread or args.thread == -1):
        cmd = "python -W ignore -u run.py" + \
              " --algo " + algo + \
              " --dataset " + dataset + \
              " --iterations " + str(iterations) + \
              " --param_s " + str(s)
        print(cmd) 
        os.system(cmd) 