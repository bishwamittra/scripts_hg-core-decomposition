# echo "Rank is: ${OMPI_COMM_WORLD_RANK}"

ulimit -t unlimited
shopt -s nullglob
numthreads=$((OMPI_COMM_WORLD_SIZE))
mythread=$((OMPI_COMM_WORLD_RANK))

# echo $numthreads
# echo $mythread

# tlimit="2000"
memlimit="4000000"
ulimit -v $memlimit


# multithread
python distribution.py --thread $mythread --max_thread $numthreads > data/output/$mythread:$(date +"%d-%m-%Y-%T".txt)  2>&1

# single thread
# python distribution.py > data/output/$mythread:$(date +"%d-%m-%Y-%T".txt)  2>&1
