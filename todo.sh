# echo "Rank is: ${OMPI_COMM_WORLD_RANK}"

ulimit -t unlimited
shopt -s nullglob
numthreads=$((OMPI_COMM_WORLD_SIZE))
mythread=$((OMPI_COMM_WORLD_RANK))

# echo $numthreads
# echo $mythread

# tlimit="2000"
# memlimit="4000000"
# ulimit -v $memlimit
# ulimit -v unlimited
ulimit -v 16000000


# multithread
python -u distribution.py --thread $mythread --max_thread $numthreads > data/output/$mythread:$(date +"%d-%m-%Y-%T".txt)  2>&1

# multithread single iteration
# python -u distribution.py --iter 1 --thread $mythread --max_thread $numthreads > data/output/$mythread:$(date +"%d-%m-%Y-%T".txt)  2>&1


# SIS Run
# python -u distribution_SIS.py --thread $mythread --max_thread $numthreads > data/output/$mythread:$(date +"%d-%m-%Y-%T".txt)  2>&1

# single thread
# python -u distribution.py > data/output/$mythread:$(date +"%d-%m-%Y-%T".txt)  2>&1

# multithread distribution_test.py single iteration
python -u distribution_test.py --iter 1 --thread $mythread --max_thread $numthreads > data/output/$mythread:$(date +"%d-%m-%Y-%T".txt)  2>&1

# multithread scalability experiments
# python -u distribution.py --scal --thread $mythread --max_thread $numthreads > data/output/$mythread:$(date +"%d-%m-%Y-%T".txt)  2>&1

# kill $(ps aux | grep 'NNdhUiT' | grep 'python' | awk '{print $2}')