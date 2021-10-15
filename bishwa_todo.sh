# python run.py --sir --algo naive_nbr --prob 0.1
# python run.py --sir --algo naive_nbr --prob 0.2
# python run.py --sir --algo naive_nbr --prob 0.3
# python run.py --sir --algo naive_nbr --prob 0.4
# python run.py --sir --algo naive_nbr --prob 0.5
# python run.py --sir --algo naive_degree --prob 0.1
# python run.py --sir --algo naive_degree --prob 0.2
# python run.py --sir --algo naive_degree --prob 0.3
# python run.py --sir --algo naive_degree --prob 0.4
# python run.py --sir --algo naive_degree --prob 0.5
# python run.py --sir --algo naive_nbr -d congress --prob 0.001
python run.py --sir --algo naive_nbr -d contact --prob 0.01
python run.py --sir --algo naive_degree -d contact --prob 0.01
python run.py --sir --algo graph_core -d contact --prob 0.01
# python run.py --sir --algo naive_nbr -d enron --prob 0.001
# python run.py --sir --algo naive_degree -d enron --prob 0.001
# python run.py --sir --algo graph_core -d enron --prob 0.001
# python run.py --sir --algo naive_degree -d congress --prob 0.001
# python run.py --sir --algo graph_core -d congress --prob 0.001
# python run.py --sir --algo graph_core -d dblp
# python run.py --sir --algo naive_degree -d dblp 
# python run.py --sir --algo naive_nbr -d dblp