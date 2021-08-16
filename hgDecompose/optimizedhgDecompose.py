from time import time
import math
from hgDecompose.Hypergraph import Hypergraph
from copy import deepcopy
from multiprocessing import Pool

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
        self.subgraph_time = 0
        self.num_subgraph_call = 0
        self.init_time = 0
        self.loop_time = 0
        self.inner_iteration = 0
        self.total_iteration = 0
        
    def preprocess(self):
        pass

    
    """
    Notes on naive nbr: 
    1) Data structure optimizations:-
        a) If possible, Replace all instances of list enumeration with generators.
        b) bucket[] => Can the values be set() instead of list()?
            => Append() ( O(1)/O(n) vs O(1) )
            => Remove() ( O(1)/O(n) vs O(n) )
            => x in set/list ( O(1)/ O(n) )
                => Soln: bucket[] => list of booleans on size n.
    """
    def naiveNBR(self, H, verbose = True):
        start_execution_time = time()

        num_nodes = 0
        
        # Initial bucket fill-up
        start_init_time = time()
        for node in H.node_iterator():
            len_neighbors = H.get_init_nbrlen(node)
            self._node_to_num_neighbors[node] = len_neighbors
            if len_neighbors not in self.bucket:
                self.bucket[len_neighbors] = set()
            self.bucket[len_neighbors].add(node)
            num_nodes += 1
        self.init_time = time() - start_init_time

        if(verbose):
            # print("\n---------- Initial neighbors -------")
            # for node in H.nodes():
            #     print(node, H.neighbors(node))
            # print()

            print("\n---------- Initial bucket -------")
            print(self.bucket)
            print()

        
        start_loop_time = time()
        for k in range(1, num_nodes + 1):
            while len(self.bucket.get(k, [])) != 0:
                v = self.bucket[k].pop()  # get first element in the
                
                if(verbose):
                    print("k:", k, "node:", v)
    
                self.core[v] = k
                nbr_v = H.neighbors(v)
                start_subgraph_time = time()

                H.removeV_transform(v, False)
                # H.removeV_transform2(v,verbose)
                self.subgraph_time += time() - start_subgraph_time
                self.num_subgraph_call += 1

                # enumerating over all neighbors of v
                for u in nbr_v:
                    self.inner_iteration += 1
                    self.total_iteration +=1
                    if (verbose):
                        print("node_to_num_neighbours: ",self._node_to_num_neighbors)
                        print("Considering neighbor", u)

                    start_neighborhood_call = time()
                    len_neighbors_u = H.get_number_of_nbrs(u)
                    self.neighborhood_call_time  += time() - start_neighborhood_call
                    self.num_neighborhood_computation += 1

                    max_value = max(len_neighbors_u, k)

                    if(verbose):
                        print("max core between", k, 'and', len_neighbors_u, "is ", max_value)
                        print("The location of", u, "is updated from", self._node_to_num_neighbors[u], "to", max_value)


                    # Move u to new location in bucket
                    start_bucket_update = time()
                    prev_idx = self._node_to_num_neighbors[u]

                    self.bucket[prev_idx].remove(u)

                    if max_value not in self.bucket:
                        self.bucket[max_value] = set()
                    self.bucket[max_value].add(u)
                    self.num_bucket_update += 1
                    self.bucket_update_time += time() - start_bucket_update
                    self._node_to_num_neighbors[u] = max_value

                    if(verbose):
                        print("-------- Updated bucket ---------")
                        print(self.bucket)
                        print()

        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time


    def naiveDeg(self, H, verbose = True):
        assert isinstance(H,Hypergraph)
        start_execution_time = time()

        nodes = list(H.nodes())
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
            for node in H.nodes():
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

                start_subgraph_time = time()
                H_temp = H.strong_subgraph(temp_nodes) # Store.... + executation time.. 
                self.subgraph_time += time() - start_subgraph_time
                self.num_subgraph_call += 1



                # enumerating over all neighbors of v
                for u in H.neighbors(v):  

                    if(verbose):
                        print(self._node_to_degree)
                        print("Considering neighbor", u)

                    start_degree_call = time()
                    degree_u = H_temp.degree(u)
                    self.degree_call_time  += time() - start_degree_call
                    self.num_degree_computation += 1
                    # How many times is neighborhood computation done? and executation time...

                    max_value = max(degree_u, k)

                    if(verbose):
                        print("max core between", k, 'and', degree_u, "is ", max_value)
                        print("The location of", u, "is updated from", self._node_to_degree[u], "to", max_value)


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

    # Interval generator function (optimized) (s is a parameter)
    def generate_intervals(self, H, s = 1, verbose = False):
        sorted_ub_set = H.sorted_ub_set # precomputed
        len_ub_set = len(sorted_ub_set)
        if(verbose):
            print('set of distinct values: ',sorted_ub_set)
            print("#distinct values: ", len(sorted_ub_set))
            print('range: ',(sorted_ub_set[-1],sorted_ub_set[0]) )
        if s >= len_ub_set:
            yield sorted_ub_set[-1] + 1, sorted_ub_set[0]
        else:
            i = s
            while i < len_ub_set:
                yield sorted_ub_set[i] + 1, sorted_ub_set[i - s]
                if i+s < len_ub_set:
                    i += s
                else:
                    if i != len_ub_set - 1:
                        yield sorted_ub_set[-1] + 1, sorted_ub_set[i]
                    i += s

    # def generate_intervals(self, llb, lub, s = 1, verbose = False):
    #     min_llb = min([llb[u] for u in llb])
    #     ub_set = set([lub[u] for u in lub]).union([min_llb - 1])
    #     sorted_ub_set = sorted(ub_set, reverse=True)
    #     if(verbose):
    #         print('set of distinct values: ',sorted_ub_set)
    #         print("#distinct values: ", len(sorted_ub_set))
    #         print('range: ',(sorted_ub_set[-1],sorted_ub_set[0]) )
    #     if s >= len(ub_set):
    #         yield sorted_ub_set[-1] + 1, sorted_ub_set[0]
    #     else:
    #         i = s
    #         while i < len(ub_set):
    #             yield sorted_ub_set[i] + 1, sorted_ub_set[i - s]
    #             if i+s < len(ub_set):
    #                 i += s
    #             else:
    #                 if i != len(ub_set) - 1:
    #                     yield sorted_ub_set[-1] + 1, sorted_ub_set[i]
    #                 i += s

    def improvedNBR(self, H, verbose = True):
        start_execution_time = time()
        
        lb1 = H.glb
        lb2 = {} # key = nodeid, value = integer.
        ub1 = H.gub

        # Initial bucket fill-up
        start_init_time = time()
        for node in H.node_iterator():
            len_neighbors = H.get_init_nbrlen(node)
            lb2[node] = H.precomputedlb2[node]
            self._node_to_num_neighbors[node] = len_neighbors
            if len_neighbors not in self.bucket:
                self.bucket[len_neighbors] = set()
            self.bucket[len_neighbors].add(node)

        self.init_time = time() - start_init_time

        if(verbose):
            print("\n---------- Initial neighbors -------")
            # for node in H.nodes():
            #     print(node, H.neighbors(node))
            # print()

            print("\n---------- Initial bucket -------")
            print(self.bucket)
            print()

        start_loop_time = time()
        for k in range(lb1, ub1):
            while len(self.bucket.get(k,[])) != 0:
                v = self.bucket[k].pop() # get first element in the
                if(verbose):
                    print("k:", k, "node:", v)
                self.core[v] = k

    
                nbr_v = H.neighbors(v)
                if (verbose):
                    print('removing ',v)
                start_subgraph_time = time()
                H.removeV_transform(v, verbose) # Store.... + executation time..
                # H.removeV_transform2(v, verbose)
                self.subgraph_time += time() - start_subgraph_time
                self.num_subgraph_call += 1

                for u in nbr_v:
                    self.total_iteration +=1
                    if lb2[u] <= k:
                        self.inner_iteration += 1
                        start_neighborhood_call = time()
                        len_neighbors_u = H.get_number_of_nbrs(u)
                        self.neighborhood_call_time += time() - start_neighborhood_call
                        self.num_neighborhood_computation += 1
                        
                        max_value = max(len_neighbors_u, k)
                        if(verbose):
                            print("max core between", k, 'and', len_neighbors_u, "is ", max_value)
                            print("The location of", u, "is updated from", self._node_to_num_neighbors[u], "to", max_value)
                        
                        start_bucket_update = time()
                        self.bucket[self._node_to_num_neighbors[u]].remove(u)

                        if max_value not in self.bucket:
                            self.bucket[max_value] = set()
                        self.bucket[max_value].add(u)
                        self.num_bucket_update += 1    
                        self.bucket_update_time += time() - start_bucket_update

                        # update new location of u
                        self._node_to_num_neighbors[u] = max_value

                    if(verbose):
                        print("-------- Updated bucket ---------")
                        print(self.bucket)
                        print()

        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time

        if(verbose):
            print("\n\nOutput")
            print(self.core)


    def improved2NBR(self, H, s = 1, verbose = True):
        """ 
        :param H -> Hypergraph
        :param s -> Integer, algorithm parameter. 
        """
        start_execution_time = time()

        # num_nodes = 0
        nodes = set()

        # glb = H.glb
        llb = {}
        # gub = H.gub
        lub = {}

        start_init_time = time()
        # Initial bucket fill-up
        for node in H.node_iterator():
            # len_neighbors = H.get_init_nbrlen(node)
            llb[node] = H.precomputedlb2[node]
            lub[node] = H.precomputedub2[node]
            # self._node_to_num_neighbors[node] = len_neighbors
            
            # if len_neighbors not in self.bucket:
            #     self.bucket[len_neighbors] = set()
            # self.bucket[len_neighbors].add(node)
            # num_nodes += 1
            nodes.add(node)

        if(verbose):
            pass
            # print("\n---------- Initial neighbors -------")
            # for node in H.nodes():
            #     print(node, H.neighbors(node))
            # print()

            # print("\n---------- Initial bucket -------")
            # print(self.bucket)
            # print()

            # print("\n -------- local lower bound --------")
            # print(llb)

        gen = self.generate_intervals(H, s = s, verbose = verbose)
        
        self.init_time = time() - start_init_time
        # if(verbose):
        #     print('local upper bound: ')
        #     print(sorted(lub.items()))
        #     print('local lower bound: ')
        #     print(sorted(llb.items()))


        final_bucket = {}
        setlb = {}
        inv_bucket = {}
        
        start_loop_time = time()
        for lower, upper in gen:
            if(verbose):
                print("Inverval [%d,%d]"%(lower, upper))

            V_kmin = [u for u in nodes if lub[u] >= lower]
            for u in V_kmin:
                if u in self.core:
                    max_val = max(lower-1, llb[u], self.core[u])
                else:
                    max_val = max(lower-1, llb[u])
                if max_val not in final_bucket:
                    final_bucket[max_val] = set()
                final_bucket[max_val].add(u)
                inv_bucket[u] = max_val
                setlb[u] = True


            start_subgraph_time = time()
            H_kmin = H.strong_subgraph(V_kmin)
            self.subgraph_time += time() - start_subgraph_time
            self.num_subgraph_call += 1


            for k in range(lower-1, upper+1):
                while len(final_bucket.get(k, [])) != 0:
                    v = final_bucket[k].pop()
                    # core[v] = k
                    if setlb[v]:
                        start_neighborhood_call = time()
                        num_nbrs_v = H_kmin.get_number_of_nbrs(v)
                        self.neighborhood_call_time  += time() - start_neighborhood_call
                        self.num_neighborhood_computation += 1

                        if num_nbrs_v not in final_bucket:
                            final_bucket[num_nbrs_v] = set()
                        final_bucket[num_nbrs_v].add(v)
                        inv_bucket[v] = num_nbrs_v
                        setlb[v] = False
                    else:
                        if k >= lower:
                            self.core[v] = k
                            setlb[v] = True
                        
                        nbrs_Hkmin = H_kmin.neighbors(v)
                        start_subgraph_time = time()
                        
                        H_kmin.removeV_transform(v, False)
                        self.subgraph_time += time() - start_subgraph_time
                        self.num_subgraph_call += 1
                        

                        for u in nbrs_Hkmin:
                            start_neighborhood_call = time()
                            len_neighbors_u = H_kmin.get_number_of_nbrs(u)
                            self.neighborhood_call_time  += time() - start_neighborhood_call
                            self.num_neighborhood_computation += 1
                    
                            max_value = max(len_neighbors_u, k)
                            start_bucket_update = time()
                            if max_value != inv_bucket[u]:
                                if max_value not in final_bucket:
                                    final_bucket[max_value] = set()
                                final_bucket[max_value].add(u)
                                prev_idx = inv_bucket[u]
                                final_bucket[prev_idx].remove(u)
                                inv_bucket[u] = max_value
                                self.num_bucket_update += 1
                            self.bucket_update_time += time() - start_bucket_update
                        
        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time

        if(verbose):
            print("\n\nOutput")
            print(self.core)
    
    def parallel_compute_core(self, arg):
        # unpacking arguments
        H = self._working_H
        lower, upper, verbose = arg
        
        final_bucket = {}
        inv_bucket = {}

        # local variables
        _local_subgraph_time = 0
        _local_num_subgraph_call = 0
        _local_neighborhood_call_time = 0
        _local_num_neighborhood_computation = 0
        _local_num_bucket_update = 0
        _local_bucket_update_time = 0
        _local_core = {}


        

        if (verbose):
            print("Inverval [%d,%d]" % (lower, upper))

        V_kmin = [u for u in H.node_iterator() if H.precomputedub2[u] >= lower]
        start_subgraph_time = time()
        H_kmin = H.strong_subgraph(V_kmin)
        _local_subgraph_time += time() - start_subgraph_time
        _local_num_subgraph_call += 1
        for u in V_kmin:
            start_neighborhood_call = time()
            num_nbrs_v = H_kmin.get_number_of_nbrs(u)
            _local_neighborhood_call_time += time() - start_neighborhood_call
            _local_num_neighborhood_computation += 1
            if num_nbrs_v not in final_bucket:
                final_bucket[num_nbrs_v] = set()
            final_bucket[num_nbrs_v].add(u)
            inv_bucket[u] = num_nbrs_v
        
        
        for k in range(lower, upper + 1):
            while len(final_bucket.get(k, [])) != 0:
                v = final_bucket[k].pop()
                # if (verbose):
                #     print('removing: ',v)
                _local_core[v] = k
                nbrs_Hkmin = H_kmin.neighbors(v)
                start_subgraph_time = time()
                H_kmin.removeV_transform(v, False)
                _local_subgraph_time += time() - start_subgraph_time
                _local_num_subgraph_call += 1
                
                for u in nbrs_Hkmin:
                    start_neighborhood_call = time()
                    len_neighbors_u = H_kmin.get_number_of_nbrs(u)
                    _local_neighborhood_call_time += time() - start_neighborhood_call
                    _local_num_neighborhood_computation += 1
                    if len_neighbors_u <= upper:
                        max_value = max(len_neighbors_u, k)
                        if max_value != inv_bucket[u]:
                            start_bucket_update = time()
                            if max_value not in final_bucket:
                                final_bucket[max_value] = set()
                            final_bucket[max_value].add(u)
                            prev_idx = inv_bucket[u]
                            final_bucket[prev_idx].remove(u)
                            inv_bucket[u] = max_value
                            _local_num_bucket_update += 1
                            _local_bucket_update_time += time() - start_bucket_update
        # print("\n")
        # print(_local_core)
        # print("\n")

        return _local_core, \
                _local_bucket_update_time, \
                _local_num_bucket_update, \
                _local_neighborhood_call_time, \
                _local_num_neighborhood_computation, \
                _local_subgraph_time, \
                _local_num_subgraph_call

    def parallel3_compute_core(self, arg):
        # unpacking arguments
        H_kmin = self._working_H
        # H_kmin = deepcopy(self._working_H)
        lower, upper, verbose = arg
        
        final_bucket = {}
        inv_bucket = {}

        # local variables
        _local_subgraph_time = 0
        _local_num_subgraph_call = 0
        _local_neighborhood_call_time = 0
        _local_num_neighborhood_computation = 0
        _local_num_bucket_update = 0
        _local_bucket_update_time = 0
        _local_core = {}

        if (verbose):
            print("Inverval [%d,%d]" % (lower, upper))

        # V_kmin = [u for u in H.node_iterator() if H.precomputedub2[u] >= lower]
        V_kmin = [u for u in H_kmin.node_iterator() if (lower <= H_kmin.precomputedub2[u] <= upper)]

        start_subgraph_time = time()
        # H_kmin = H.strong_subgraph(V_kmin)
        # H_kmin = deepcopy(H)
        _local_subgraph_time += time() - start_subgraph_time
        _local_num_subgraph_call += 1
        for u in V_kmin:
            start_neighborhood_call = time()
            num_nbrs_v = H_kmin.get_number_of_nbrs(u)
            _local_neighborhood_call_time += time() - start_neighborhood_call
            _local_num_neighborhood_computation += 1
            if num_nbrs_v not in final_bucket:
                final_bucket[num_nbrs_v] = set()
            final_bucket[num_nbrs_v].add(u)
            inv_bucket[u] = num_nbrs_v
        
        
        for k in range(lower, upper + 1):
            while len(final_bucket.get(k, [])) != 0:
                v = final_bucket[k].pop()
                # if (verbose):
                #     print('removing: ',v)
                _local_core[v] = k
                nbrs_Hkmin = H_kmin.neighbors(v)
                start_subgraph_time = time()
                H_kmin.removeV_transform(v, False)
                _local_subgraph_time += time() - start_subgraph_time
                _local_num_subgraph_call += 1
                
                for u in nbrs_Hkmin:
                    if u not in V_kmin:
                        continue
                    start_neighborhood_call = time()
                    len_neighbors_u = H_kmin.get_number_of_nbrs(u)
                    _local_neighborhood_call_time += time() - start_neighborhood_call
                    _local_num_neighborhood_computation += 1
                    if len_neighbors_u <= upper:
                        max_value = max(len_neighbors_u, k)
                        if max_value != inv_bucket[u]:
                            start_bucket_update = time()
                            if max_value not in final_bucket:
                                final_bucket[max_value] = set()
                            final_bucket[max_value].add(u)
                            prev_idx = inv_bucket[u]
                            final_bucket[prev_idx].remove(u)
                            inv_bucket[u] = max_value
                            _local_num_bucket_update += 1
                            _local_bucket_update_time += time() - start_bucket_update
        # print("\n")
        # print(_local_core)
        # print("\n")

        return _local_core, \
                _local_bucket_update_time, \
                _local_num_bucket_update, \
                _local_neighborhood_call_time, \
                _local_num_neighborhood_computation, \
                _local_subgraph_time, \
                _local_num_subgraph_call

    def parallel_improved2NBR(self, H, s = 1, num_threads = 4, verbose = True):
        """
        :param H -> Hypergraph
        :param s -> Integer, algorithm parameter.
        """
        start_execution_time = time()

        # num_nodes = 0
        # nodes = set()

        # glb = H.glb
        llb = {}
        # gub = H.gub
        lub = {}

        start_init_time = time()
       
        for node in H.node_iterator():
           
            # len_neighbors = H.get_init_nbrlen(node)
            
            llb[node] = H.precomputedlb2[node]
            lub[node] = H.precomputedub2[node]
            
            # self._node_to_num_neighbors[node] = len_neighbors
            
            # if len_neighbors not in self.bucket:
            #     self.bucket[len_neighbors] = set()
            # self.bucket[len_neighbors].add(node)
            # num_nodes += 1
            # nodes.add(node)

        if(verbose):
            pass
            # print("\n---------- Initial neighbors -------")
            # for node in H.nodes():
            #     print(node, H.neighbors(node))
            # print()

            # print("\n---------- Initial bucket -------")
            # print(self.bucket)
            # print()

            # print("\n -------- local lower bound --------")
            # print(llb)

        gen = self.generate_intervals(H, s = s, verbose = verbose)
        
        self.init_time = time() - start_init_time
        # if(verbose):
        #     print('local upper bound: ')
        #     print(sorted(lub.items()))
        #     print('local lower bound: ')
        #     print(sorted(llb.items()))
        
        start_loop_time = time()
        # for lower, upper in gen:
        #     # print(lower,upper)
        #     self.parallel_compute_core(H, lower, upper, verbose)
        
        # Parallel run
        self._working_H = H
        # arguments = 
        # num_threads = len(arguments)
        # num_threads = 4
        with Pool(num_threads) as p:
            return_values = p.map(self.parallel_compute_core, [(lower, upper, verbose) for lower, upper in gen])

        # Retrieving return values
        for val in return_values:
            _local_core, \
            _local_bucket_update_time, \
            _local_num_bucket_update, \
            _local_neighborhood_call_time, \
            _local_num_neighborhood_computation, \
            _local_subgraph_time, \
            _local_num_subgraph_call = val

            for v, k in _local_core.items():
                self.core[v] = k
            self.bucket_update_time += _local_bucket_update_time
            self.num_bucket_update += _local_num_bucket_update
            self.neighborhood_call_time += _local_neighborhood_call_time
            self.num_neighborhood_computation += _local_num_neighborhood_computation
            self.subgraph_time += _local_subgraph_time
            self.num_subgraph_call += _local_num_subgraph_call



            
        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time

        if(verbose):
            print("\n\nOutput")
            print(self.core)

    def parallel_improved3NBR(self, H, s = 1, num_threads = 4, verbose = True):
        """
        :param H -> Hypergraph
        :param s -> Integer, algorithm parameter.
        Does not compute strong subhypergraph.
        """
        start_execution_time = time()

        # num_nodes = 0
        # nodes = set()

        # glb = H.glb
        llb = {}
        # gub = H.gub
        lub = {}

        start_init_time = time()
        # Initial bucket fill-up
        for node in H.node_iterator():
           
            # len_neighbors = H.get_init_nbrlen(node)
            
            llb[node] = H.precomputedlb2[node]
            lub[node] = H.precomputedub2[node]
            
            # self._node_to_num_neighbors[node] = len_neighbors
            
            # if len_neighbors not in self.bucket:
            #     self.bucket[len_neighbors] = set()
            # self.bucket[len_neighbors].add(node)
            # num_nodes += 1
            # nodes.add(node)

        if(verbose):
            pass
            # print("\n---------- Initial neighbors -------")
            # for node in H.nodes():
            #     print(node, H.neighbors(node))
            # print()

            # print("\n---------- Initial bucket -------")
            # print(self.bucket)
            # print()

            # print("\n -------- local lower bound --------")
            # print(llb)

        gen = self.generate_intervals(H, s = s, verbose = verbose)
        
        self.init_time = time() - start_init_time
        # if(verbose):
        #     print('local upper bound: ')
        #     print(sorted(lub.items()))
        #     print('local lower bound: ')
        #     print(sorted(llb.items()))
        
        start_loop_time = time()
        # for lower, upper in gen:
        #     # print(lower,upper)
        #     self.parallel_compute_core(H, lower, upper, verbose)
        
        # Parallel run
        self._working_H = H
        # arguments = [(lower, upper, verbose) for lower, upper in gen]
        with Pool(num_threads) as p:
            return_values = p.map(self.parallel3_compute_core, [(lower, upper, verbose) for lower, upper in gen])

        # Retrieving return values
        for val in return_values:
            _local_core, \
            _local_bucket_update_time, \
            _local_num_bucket_update, \
            _local_neighborhood_call_time, \
            _local_num_neighborhood_computation, \
            _local_subgraph_time, \
            _local_num_subgraph_call = val

            for v, k in _local_core.items():
                self.core[v] = k
            self.bucket_update_time += _local_bucket_update_time
            self.num_bucket_update += _local_num_bucket_update
            self.neighborhood_call_time += _local_neighborhood_call_time
            self.num_neighborhood_computation += _local_num_neighborhood_computation
            self.subgraph_time += _local_subgraph_time
            self.num_subgraph_call += _local_num_subgraph_call



            
        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time

        if(verbose):
            print("\n\nOutput")
            print(self.core)