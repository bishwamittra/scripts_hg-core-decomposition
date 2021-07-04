from hgDecompose import utils
from time import time



class HGDecompose():
    def __init__(self):
        self.bucket = {}
        self.core = {}
        self._node_to_num_neighbors = {} # inverse bucket
        self._node_to_degree = {}
        self.execution_time = 0
        self.bucket_update_time = 0
        self.neighborhood_call_time = 0
        self.degree_call_time = 0
        self.num_neighborhood_computation = 0
        self.num_degree_computation = 0
        self.num_bucket_update = 0


    def preprocess(self):
        pass

    def naiveNBR(self, H, verbose = True):
        start_execution_time = time()

        nodes = list(H.nodes)
        num_nodes = len(nodes)

        # Initial bucket fill-up
        for node in nodes:
            neighbors = list(H.neighbors(node))
            len_neighbors = len(neighbors)  # this computation can be repeated
            # node_to_neighbors[node] = neighbors
            self._node_to_num_neighbors[node] = len_neighbors
            # print(node, neighbors)
            if len_neighbors not in self.bucket:
                self.bucket[len_neighbors] = [node]
            else:
                self.bucket[len_neighbors].append(node)


        if(verbose):
            print("\n---------- Initial neighbors -------")
            for node in H.nodes:
                print(node, H.neighbors(node))
            print()

            print("\n---------- Initial bucket -------")
            print(self.bucket)
            print()

        

        for k in range(1, num_nodes + 1):

            while len(self.bucket.get(k, [])) != 0:
                v = self.bucket[k].pop(0)  # get first element in the

                if(verbose):
                    print("k:", k, "node:", v)
    
                self.core[v] = k
                temp_nodes = nodes[:] 
                temp_nodes.remove(v) 

                H_temp = utils.strong_subgraph(H, temp_nodes) # Store.... + executation time.. 

                # enumerating over all neighbors of v
                for u in utils.get_nbrs(H, v):  

                    if(verbose):
                        print(self._node_to_num_neighbors)
                        print("Considering neighbor", u)

                    start_neighborhood_call = time()
                    len_neighbors_u = utils.get_number_of_nbrs(H_temp, u)
                    self.neighborhood_call_time  += time() - start_neighborhood_call
                    self.num_neighborhood_computation += 1
                    # How many times is neighborhood computation done? and executation time...

                    max_value = max(len_neighbors_u, k)

                    if(verbose):
                        print("max core between", k, 'and', len_neighbors_u, "is ", max_value)
                        print("The location of", u, "is updated from", self._node_to_num_neighbors[u], "to", max_value)


                    # Move u to new location in bucket
                    start_bucket_update = time()
                    self.bucket[self._node_to_num_neighbors[u]].remove(u)
                    if max_value not in self.bucket:
                        # TODO does code reach here?
                        self.bucket[max_value] = [u]
                    else:
                        self.bucket[max_value].append(u)
                        self.num_bucket_update += 1
                    self.bucket_update_time += time() - start_bucket_update
                        
                    # How many times is bucket updated + executation time??? Store...

                    self._node_to_num_neighbors[u] = max_value

                    if(verbose):
                        print("-------- Updated bucket ---------")
                        print(self.bucket)
                        print()

                nodes = temp_nodes
                H = H_temp


        self.execution_time = time() - start_execution_time


    def naiveDeg(self, H, verbose = True):
        start_execution_time = time()

        nodes = list(H.nodes)
        num_nodes = len(nodes)

        # Initial bucket fill-up
        max_degree = -1
        for node in nodes:

            degree = H.degree(node)
            if(degree > max_degree):
                max_degree = degree
            self._node_to_degree[node] = degree
            # print(node, neighbors)
            if degree not in self.bucket:
                self.bucket[degree] = [node]
            else:
                self.bucket[degree].append(node)


        if(verbose):
            print("\n---------- Initial neighbors -------")
            for node in H.nodes:
                print(node, H.neighbors(node))
            print()

            print("\n---------- Initial bucket -------")
            print(self.bucket)
            print()

        

        for k in range(1, max_degree + 1):

            while len(self.bucket.get(k, [])) != 0:
                v = self.bucket[k].pop(0)  # get first element in the

                if(verbose):
                    print("k:", k, "node:", v)
    
                self.core[v] = k
                temp_nodes = nodes[:] 
                temp_nodes.remove(v) 

                H_temp = utils.strong_subgraph(H, temp_nodes) # Store.... + executation time.. 

                # enumerating over all neighbors of v
                for u in utils.get_nbrs(H, v):  

                    if(verbose):
                        print(self._node_to_degree)
                        print("Considering neighbor", u)

                    start_degree_call = time()
                    degree_u = utils.get_degree(H_temp, u)
                    self.degree_call_time  += time() - start_degree_call
                    self.num_degree_computation += 1
                    # How many times is neighborhood computation done? and executation time...

                    max_value = max(degree_u, k)

                    if(verbose):
                        print("max core between", k, 'and', degree_u, "is ", max_value)
                        print("The location of", u, "is updated from", self._node_to_num_neighbors[u], "to", max_value)


                    # Move u to new location in bucket
                    start_bucket_update = time()
                    self.bucket[self._node_to_degree[u]].remove(u)
                    if max_value not in self.bucket:
                        # TODO does code reach here?
                        self.bucket[max_value] = [u]
                    else:
                        self.bucket[max_value].append(u)
                        self.num_bucket_update += 1
                    self.bucket_update_time += time() - start_bucket_update
                        
                    # How many times is bucket updated + executation time??? Store...

                    self._node_to_degree[u] = max_value

                    if(verbose):
                        print("-------- Updated bucket ---------")
                        print(self.bucket)
                        print()

                nodes = temp_nodes
                H = H_temp


        self.execution_time = time() - start_execution_time






