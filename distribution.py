
import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--thread", help="index of thread", default=-1, type=int)
parser.add_argument("--max_thread", help="maximum number of thread", default=1, type=int)
args = parser.parse_args()


algo_list = ['naive_nbr', 'naive_degree', 'improved2_nbr']
dataset_list = ['default', 'syn']
iterations = 10



# all combination of experiments
configurations = []
for algo in algo_list:
    for dataset in dataset_list:
        configurations.append((algo, dataset))



# print(len(configurations))
# distributing among threads
for i, configuration in enumerate(configurations):
    algo, dataset = configuration
    if(i%args.max_thread == args.thread or args.thread == -1):
        cmd = "python -W ignore run.py" + \
              " --algo " + algo + \
              " --dataset " + dataset + \
              " --iterations " + str(iterations)
        print(cmd) 
        os.system(cmd) 