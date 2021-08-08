
import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--thread", help="index of thread", default=-1, type=int)
parser.add_argument("--max_thread", help="maximum number of thread", default=1, type=int)
args = parser.parse_args()

# ['enron', 'congress', 'contact', 'syn', 'bin_1', 'bin_2', 'bin_4', 'bin_5']
# algo_list = ['naive_nbr', 'improved_nbr', 'improved2_nbr', 'naive_degree']
algo_list = ['naive_nbr', 'improved_nbr', 'naive_degree']
dataset_list = ['syn', 'bin_1', 'bin_2', 'bin_4', 'bin_5', 'enron', 'congress', 'contact', 'dblp','amazon']
param_s_dict = {
                'syn':(1,7), 'bin_1':(27,56), 'bin_2':(186,265), 'bin_4':(21,44),
                 'bin_5':(130,195), 'enron':(1,934), 'congress':(3,1360), 'contact':(20,134), 
                 'dblp': (1,10), 'amazon': (1,10)
                 }
# param_s = [i+1 for i in range(10)]
iterations = 10
num_divisions = 20

# small exp
# iterations = 1
# dataset_list = ['default', 'syn']

# assert iterations > 1

# all combination of experiments
configurations = []
for dataset in dataset_list:
    for algo in algo_list:
        if(algo in ['improved2_nbr']): # Additional param    
            delta = int((param_s_dict[dataset][1]  - param_s_dict[dataset][0])/num_divisions)
            
            for s in range(param_s_dict[dataset][0],param_s_dict[dataset][1]+1, max(delta,1)):    
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

# TO DO: ignore assertion -O