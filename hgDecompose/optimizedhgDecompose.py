from time import time
import math
from hgDecompose.Hypergraph import Hypergraph
from hgDecompose.IncidenceRep import HypergraphL
from copy import deepcopy
from multiprocessing import Pool
from hgDecompose.utils import operator_H, par_operator_H
from hgDecompose.heapdict import heapdict
# from tests.verify_kcore import *

class HGDecompose():
    def __init__(self):
        # self.bucket = {}
        self.core = {}
        # self._node_to_num_neighbors = {} # inverse bucket
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
        self.core_correct_time = 0
        self.h_index_time = 0
        self.max_n = 0 # For #iterations vs dataset barplot
        self.core_correctionvol_n = [] #  core_corrections volume per iteration => Ammount of core_correction done. => Relation with runtime
        self.core_correction_volume = 0 # For core_correction volume vs dataset plot
        self.reduction_hhat_n = [] # [ hhat^{n-1} - hhat^{n}, for n \in [1, tau] ] => Convergence plot.

    def preprocess(self):
        pass
    
    def LLCSAT(self, H, u, core_u, core_dict):
        nbrhood_u_plus = set()
        for e_id in H.inc_dict[u]:
            edge = H.get_edge_byindex(e_id)
            flag = True
            for v in edge: 
                if u != v:
                    if core_dict[v] < core_u: 
                        flag = False
                        break
            if flag:
                nbrhood_u_plus = nbrhood_u_plus.union(edge)
                nbrhood_u_plus.remove(u)

        if len(nbrhood_u_plus) >= core_u: 
            return True
        else:
            return False

    def bst_core_correct(self, H, u, h_minus, h_plus, core_u, core_dict):
        LLCSAT_h_min = self.LLCSAT(H, u, h_minus, core_dict)
        LLCSAT_h_plus = self.LLCSAT(H, u, h_plus, core_dict)
        if LLCSAT_h_min == LLCSAT_h_plus == True:
            return h_plus 
        elif LLCSAT_h_min == LLCSAT_h_plus == False:
            return h_minus - 1
        else: 
            mid = math.ceil((h_minus + h_plus)/2)
            llcmid = self.LLCSAT(H, u, mid, core_dict)
            if (llcmid):
                h_minus = mid + 1
            else:
                h_plus = mid - 1
            return self.bst_core_correct(H, u, h_minus, h_plus, core_u, core_dict)

    def iterative_core_correct(self, H, u, core_u, core_dict):
        core_u = core_u - 1
        while not self.LLCSAT(H, u, core_u, core_dict):
            core_u = core_u - 1
        return core_u 

    def recursive_core_correct(self, H, u, core_u, core_dict):
        """ 
        Verify if core_u locally satisfies the property that the induced sub_neighborhood of u has at least u vertices. 
        If true returns core_u, If False, returns the correctd core_value.
        """
        core_u = core_u - 1
        if not self.LLCSAT(H, u, core_u, core_dict):
            return self.recursive_core_correct(H, u, core_u, core_dict)
        else:
            return core_u
        
    def local_core(self, H, verbose = True):
        start_execution_time = time()
        start_init_time = time()
        for node in H.init_node_iterator():
            len_neighbors = H.get_init_nbrlen(node)
            self.core[node] = len_neighbors
            
        self.init_time = time() - start_init_time  
        if(verbose):
            print("Init core")
            print(self.core)

        start_loop_time = time()
        k = 0
        while True:
            hn_minus_hhatn = 0
            hn_1_minus_hn = 0
            if (verbose):
                print("Iteration: ", k)
            
            flag = True

            start_inner_time = time()
            for node in H.init_node_iterator():
                H_value = operator_H([self.core[j] for j in H.get_init_nbr(node)])
                self.core[node] = min(H_value, self.core[node])
                if H_value < self.core[node]:
                    hn_1_minus_hn += (self.core[node] - H_value)
                    self.core[node] = H_value 
            self.h_index_time += (time() - start_inner_time)

            
            start_core_correct_time = time()
            for node in H.init_node_iterator():   
                if not self.LLCSAT(H, node, self.core[node], self.core):   
                    flag = False  
                    hhatn = self.recursive_core_correct(H, node, self.core[node], self.core)
                    hn_minus_hhatn += (self.core[node] - hhatn)
                    self.core[node]  = hhatn
            self.core_correct_time += (time() - start_core_correct_time)
            self.core_correctionvol_n.append(hn_minus_hhatn)
            self.reduction_hhat_n.append(hn_1_minus_hn + hn_minus_hhatn)

            k+=1
            if flag:
                break

        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time
        print("Iteration: ", k)
        self.core_correction_volume = sum(self.core_correctionvol_n)
        self.max_n = k

    # def bst_local_core(self, H, verbose = True):
    #     if verbose:
    #         print('tau: ', H.get_M())

    #     start_execution_time = time()
    #     start_init_time = time()
    #     for node in H.init_node_iterator():
    #         len_neighbors = H.get_init_nbrlen(node)
    #         self.core[node] = len_neighbors
            
    #     self.init_time = time() - start_init_time  
    #     if(verbose):
    #         print("Init core")
    #         print(self.core)

    #     start_loop_time = time()
    
    #     k = 0
        
    #     while True:
    #         if (verbose):
    #             print("Iteration: ", k)
            
    #         flag = True

    #         start_inner_time = time()
    #         for node in H.init_node_iterator():
    #             H_value = operator_H([self.core[j] for j in H.get_init_nbr(node)])
    #             self.core[node] = min(H_value, self.core[node])
    #         self.h_index_time += (time() - start_inner_time)

            
    #         start_core_correct_time = time()
    #         for node in H.init_node_iterator():
    #             if not self.LLCSAT(H, node, self.core[node], self.core):   
    #                 flag = False  
    #                 self.core[node] = self.bst_core_correct(H,node, H.llb[node], self.core[node], self.core[node], self.core)
    #         self.core_correct_time += (time() - start_core_correct_time)
    #         k+=1
    #         if flag:
    #             break
    #     self.loop_time = time() - start_loop_time
    #     self.execution_time = time() - start_execution_time
    #     self.max_n = k
    #     # print("Iteration: ", k)


    def iterative_local_core(self, H, verbose = True):
        
        start_execution_time = time()

        start_init_time = time()
        for node in H.init_node_iterator():
            len_neighbors = H.get_init_nbrlen(node)
            self.core[node] = len_neighbors

        self.init_time = time() - start_init_time  
        if(verbose):
            print("Init core")
            print(self.core)

        # Main loop
        start_loop_time = time()
        k = 0
        while True:
            hn_minus_hhatn = 0
            hn_1_minus_hn = 0
            if (verbose):
                print("Iteration: ", k)

            flag = True

            start_inner_time = time()
            for node in H.init_node_iterator():
                H_value = operator_H([self.core[j] for j in H.get_init_nbr(node)])
                if H_value < self.core[node]:
                    hn_1_minus_hn += (self.core[node] - H_value)
                    self.core[node] = H_value 
            self.h_index_time += (time() - start_inner_time)

            start_core_correct_time = time()
            for node in H.init_node_iterator():
                if not self.LLCSAT(H, node, self.core[node], self.core):   
                    flag = False  
                    hhatn = self.iterative_core_correct(H, node, self.core[node], self.core)
                    hn_minus_hhatn += (self.core[node] - hhatn)
                    self.core[node]  = hhatn

            self.core_correct_time += (time() - start_core_correct_time)
            self.core_correctionvol_n.append(hn_minus_hhatn)
            self.reduction_hhat_n.append(hn_1_minus_hn + hn_minus_hhatn)
            
            k+=1
            if flag:
                break

        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time
        self.core_correction_volume = sum(self.core_correctionvol_n)
        self.max_n = k
        # print("Iteration: ", k)

    def improved_local_core(self, H, verbose = True):
        if verbose:
            print('tau: ', H.get_M())

        start_execution_time = time()
        # num_nodes = 0
        # Init
        start_init_time = time()
        dirty = heapdict()
        for node in H.init_node_iterator():
            len_neighbors = H.get_init_nbrlen(node)
            self.core[node] = len_neighbors
            dirty[node] = len_neighbors
            # num_nodes += 1
        self.init_time = time() - start_init_time  
        if(verbose):
            print("Init core")
            print(self.core)

        # Main loop
        start_loop_time = time()
    
        k = 0
        
        while True:
            hn_1_minus_hn = 0 
            hn_minus_hhatn = 0
            if (verbose):
                print("Iteration: ", k)
            flag = True
            start_inner_time = time()
            for node in H.init_node_iterator():
                H_value = operator_H([self.core[j] for j in H.get_init_nbr(node)])
                if H_value < self.core[node]:
                    hn_1_minus_hn += (self.core[node] - H_value)
                    self.core[node] = H_value 
                    dirty[node] = self.core[node]
                # else:
                #     if node in dirty:
                #         dirty.remove(node)
            # print(dirty)
            self.h_index_time += (time() - start_inner_time)
                # if(verbose):
                #     print("k:", k, "node:", node, "c[]=",self.core[node])
            
            start_core_correct_time = time()
            dirty2 = heapdict()
            while len(dirty):
                node, prev_core = dirty.popitem()
                if not self.LLCSAT(H, node, self.core[node], self.core):   
                    flag = False
                    hhatn = self.iterative_core_correct(H, node, self.core[node], self.core)
                    hn_minus_hhatn += (self.core[node] - hhatn)
                    dirty2[node]  = self.core[node] = hhatn
                    # for u in H.init_nbr[node]:
                    #     LLCSAT_u = self.LLCSAT(H, u, self.core[u], self.core)
                    #     if not LLCSAT_u:
                    #         dirty2[u] = self.core[node]
                else:
                    dirty2[node] = prev_core
            dirty = dirty2
            # print('->',dirty)
            # core_corrected_bucket = set()
            # for node in H.init_node_iterator():
            #     if node not in core_corrected_bucket:          
            #         if not self.LLCSAT(H, node, self.core[node], self.core):   
            #             prev_core = self.core[node] 
            #             flag = False
            #             self.core[node] = self.iterative_core_correct(H, node, self.core[node], self.core)
            #             core_corrected_bucket.add(node)
                    
            #             for u in H.init_nbr[node]:
            #                 if self.core[u] > self.core[node] and self.core[u] <= prev_core: 
            #                     # Instead of checking LLCSAT again assume they must be corrected.
            #                     self.core[node] = self.iterative_core_correct(H, u, self.core[u], self.core)
            #                     core_corrected_bucket.add(u)
            self.core_correct_time += (time() - start_core_correct_time)
            self.core_correctionvol_n.append(hn_minus_hhatn)
            self.reduction_hhat_n.append(hn_1_minus_hn + hn_minus_hhatn)
            k+=1
            if flag:
                break

        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time
        self.core_correction_volume = sum(self.core_correctionvol_n)
        self.max_n = k
        
    def opt_LCCSAT(self, H, u, core_u):
        """LCCSAT check using by keeping track of incident edge min(h_indx)"""
        assert isinstance(H, HypergraphL)

        Nplus = set()
        for e_id in H.inc_edgeId_iterator(u):
            if  H.get_min_hindex(e_id = e_id) >= core_u: 
                edge = H.get_edge_byindex(e_id)
                Nplus = Nplus.union(edge)
        if len(Nplus):
            Nplus.remove(u)
            if len(Nplus) >= core_u: 
                return True
            else:
                return False
        else:
            return False

    def opt_local_core(self, H, verbose = True):
        assert isinstance(H, HypergraphL)

        start_execution_time = time()
        start_init_time = time()
        # dirty = heapdict()
        for node in H.init_node_iterator():
            len_neighbors = H.get_init_nbrlen(node)
            self.core[node] = len_neighbors
            # dirty[node] = len_neighbors
            # num_nodes += 1
        self.init_time = time() - start_init_time  
        if(verbose):
            print("Init core")
            print(self.core)

        # Main loop
        start_loop_time = time()
        k = 0
        while True:
            hn_1_minus_hn = 0 
            hn_minus_hhatn = 0
            if (verbose):
                print("Iteration: ", k)
            flag = True
            start_inner_time = time()
            for node in H.init_node_iterator():
                H_value = operator_H([self.core[j] for j in H.init_nbr_iterator(node)])
                if H_value < self.core[node]:
                    hn_1_minus_hn += (self.core[node] - H_value)
                    self.core[node] = H_value
                    H.update_min_hindex(node, H_value)
                # else:
                #     self.core[node] = self.core[node]
                # dirty[node] = self.core[node]

            # print(dirty)
            self.h_index_time += (time() - start_inner_time)
                # if(verbose):
                #     print("k:", k, "node:", node, "c[]=",self.core[node])
            
            start_core_correct_time = time()
            # dirty2 = heapdict()
            # while len(dirty):
            #     node, prev_core = dirty.popitem()
            #     if not self.LLCSAT(H, node, self.core[node], self.core):   
            #         flag = False
            #         self.core[node] = self.iterative_core_correct(H, node, self.core[node], self.core)
            #         dirty2[node] = self.core[node]
            #     else:
            #         dirty2[node] = prev_core
            # dirty = dirty2
            # hhatn = {}
            for node in H.init_node_iterator():
                # if not self.LLCSAT(H, node, self.core[node], self.core):
                if not self.opt_LCCSAT(H, node, self.core[node]):   
                    flag = False
                    # self.core[node] = self.iterative_core_correct(H, node, self.core[node], self.core)
                    # hhatn[node] = self.iterative_core_correct(H, node, self.core[node], self.core)
                    hhatn = self.iterative_core_correct(H, node, self.core[node], self.core)
                    hn_minus_hhatn += (self.core[node] - hhatn)
                    self.core[node]  = hhatn

                    # H.update_min_hindex(node, hhatn[node])
                    H.update_min_hindex(node, self.core[node])
                    
                    # for u in H.init_nbr[node]:
                    #     if self.core[u] > self.core[node] and self.core[u] <= prev_core: 
                    #         # Instead of checking LLCSAT again assume they must be corrected.
                    #         self.core[node] = self.iterative_core_correct(H, u, self.core[u], self.core)
                    #         core_corrected_bucket.add(u)
            self.core_correct_time += (time() - start_core_correct_time)
            self.core_correctionvol_n.append(hn_minus_hhatn)
            self.reduction_hhat_n.append(hn_1_minus_hn + hn_minus_hhatn)
            # for node in hhatn:
            #     self.core[node] = hhatn[node]
            k+=1
            if flag:
                break

        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time
        self.core_correction_volume = sum(self.core_correctionvol_n)
        self.max_n = k
        # print('opt_local_core: ', k)

    def naiveNBR(self, H, verbose = True):
        start_execution_time = time()
        num_nodes = 0
        _node_to_num_neighbors = {}
        bucket = {}
        # Initial bucket fill-up
        start_init_time = time()
        for node in H.init_node_iterator():
            len_neighbors = H.get_init_nbrlen(node)
            _node_to_num_neighbors[node] = len_neighbors
            if len_neighbors not in bucket:
                bucket[len_neighbors] = set()
            bucket[len_neighbors].add(node)
            num_nodes += 1
        self.init_time = time() - start_init_time

        if(verbose):
            # print("\n---------- Initial neighbors -------")
            # for node in H.nodes():
            #     print(node, H.neighbors(node))
            # print()

            print("\n---------- Initial bucket -------")
            print(bucket)
            print()

        
        start_loop_time = time()
        for k in range(1, num_nodes + 1):
            while len(bucket.get(k, [])) != 0:
                v = bucket[k].pop()  # get first element in the
                
                if(verbose):
                    print("k:", k, "node:", v)
    
                self.core[v] = k
                
                start_neighborhood_call = time()
                nbr_v = H.neighbors(v)
                self.neighborhood_call_time += time() - start_neighborhood_call
                self.num_neighborhood_computation += 1

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
                        print("node_to_num_neighbours: ",_node_to_num_neighbors)
                        print("Considering neighbor", u)

                    start_neighborhood_call = time()
                    len_neighbors_u = H.get_number_of_nbrs(u)
                    self.neighborhood_call_time  += time() - start_neighborhood_call
                    self.num_neighborhood_computation += 1

                    max_value = max(len_neighbors_u, k)

                    if(verbose):
                        print("max core between", k, 'and', len_neighbors_u, "is ", max_value)
                        print("The location of", u, "is updated from", _node_to_num_neighbors[u], "to", max_value)


                    # Move u to new location in bucket
                    start_bucket_update = time()
                    prev_idx = _node_to_num_neighbors[u]

                    bucket[prev_idx].remove(u)

                    if max_value not in bucket:
                        bucket[max_value] = set()
                    bucket[max_value].add(u)
                    self.num_bucket_update += 1
                    self.bucket_update_time += time() - start_bucket_update
                    _node_to_num_neighbors[u] = max_value

                    if(verbose):
                        print("-------- Updated bucket ---------")
                        print(bucket)
                        print()
        # print(self.core)
        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time

    def naiveDeg(self, H, verbose = True):
        assert isinstance(H,Hypergraph)
        start_execution_time = time()
        bucket = {}
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
            if degree not in bucket:
                bucket[degree] = [node]
            else:
                bucket[degree].append(node)


        if(verbose):
            print("\n---------- Initial neighbors -------")
            for node in H.nodes():
                print(node, H.neighbors(node))
            print()

            print("\n---------- Initial bucket -------")
            print(bucket)
            print()

        

        for k in range(1, max_degree + 1):

            while len(bucket.get(k, [])) != 0:
                v = bucket[k].pop(0)  # get first element in the

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
                    bucket[self._node_to_degree[u]].remove(u)
                    if max_value not in bucket:
                        # TODO does code reach here?
                        bucket[max_value] = [u]
                    else:
                        bucket[max_value].append(u)
                    self.num_bucket_update += 1
                    self.bucket_update_time += time() - start_bucket_update
                        
                    # How many times is bucket updated + executation time??? Store...

                    self._node_to_degree[u] = max_value

                    if(verbose):
                        print("-------- Updated bucket ---------")
                        print(bucket)
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

    # def improvedNBR_buggy(self, H, verbose = True):
    #     start_execution_time = time()
        #   bucket = {}
    #     lb1 = H.glb
    #     lb2 = {} # key = nodeid, value = integer.
    #     ub1 = H.gub

    #     # Initial bucket fill-up
    #     start_init_time = time()
    #     for node in H.init_node_iterator():
    #         len_neighbors = H.get_init_nbrlen(node)
    #         lb2[node] = H.llb[node]
    #         self._node_to_num_neighbors[node] = len_neighbors
    #         if len_neighbors not in bucket:
    #             bucket[len_neighbors] = set()
    #         bucket[len_neighbors].add(node)

    #     self.init_time = time() - start_init_time

    #     if(verbose):
    #         print("\n---------- Initial neighbors -------")
    #         # for node in H.nodes():
    #         #     print(node, H.neighbors(node))
    #         # print()

    #         print("\n---------- Initial bucket -------")
    #         print(bucket)
    #         print()

    #     start_loop_time = time()
    #     for k in range(lb1, ub1):
    #         while len(bucket.get(k,[])) != 0:
    #             v = bucket[k].pop() # get first element in the
    #             if(verbose):
    #                 print("k:", k, "node:", v)
    #             self.core[v] = k

    
    #             nbr_v = H.neighbors(v)
    #             if (verbose):
    #                 print('removing ',v)
    #             start_subgraph_time = time()
    #             H.removeV_transform(v, verbose) # Store.... + executation time..
    #             # H.removeV_transform2(v, verbose)
    #             self.subgraph_time += time() - start_subgraph_time
    #             self.num_subgraph_call += 1

    #             for u in nbr_v:
    #                 self.total_iteration +=1
    #                 if lb2[u] <= k:
    #                     self.inner_iteration += 1
    #                     start_neighborhood_call = time()
    #                     len_neighbors_u = H.get_number_of_nbrs(u)
    #                     self.neighborhood_call_time += time() - start_neighborhood_call
    #                     self.num_neighborhood_computation += 1
                        
    #                     max_value = max(len_neighbors_u, k)
    #                     if(verbose):
    #                         print("max core between", k, 'and', len_neighbors_u, "is ", max_value)
    #                         print("The location of", u, "is updated from", self._node_to_num_neighbors[u], "to", max_value)
                        
    #                     start_bucket_update = time()
    #                     bucket[self._node_to_num_neighbors[u]].remove(u)

    #                     if max_value not in bucket:
    #                         bucket[max_value] = set()
    #                     bucket[max_value].add(u)
    #                     self.num_bucket_update += 1    
    #                     self.bucket_update_time += time() - start_bucket_update

    #                     # update new location of u
    #                     self._node_to_num_neighbors[u] = max_value

    #                 if(verbose):
    #                     print("-------- Updated bucket ---------")
    #                     print(bucket)
    #                     print()

    #     self.loop_time = time() - start_loop_time
    #     self.execution_time = time() - start_execution_time

    #     if(verbose):
    #         print("\n\nOutput")
    #         print(self.core)

    def improvedNBR(self, H, verbose=True):
        """ Arijits paper version"""
        start_execution_time = time()
        bucket = {}
        lb1 = H.glb
        ub1 = H.gub
        inverse_bucket = {}
        setlb = {}
        # Initial bucket fill-up
        start_init_time = time()
        for node in H.init_node_iterator():
            # lb = max(H.llb[node],lb1)
            lb = H.llb[node]
            inverse_bucket[node] = lb
            if lb not in bucket:
                bucket[lb] = set()
            bucket[lb].add(node)
            setlb[node] = True

        self.init_time = time() - start_init_time

        if (verbose):
            print("\n---------- Initial neighbors -------")
            # for node in H.nodes():
            #     print(node, H.neighbors(node))
            # print()

            print("\n---------- Initial bucket -------")
            print(bucket)
            print()

        start_loop_time = time()
        for k in range(lb1, ub1+1):
            while len(bucket.get(k, [])) != 0:
                v = bucket[k].pop()  # get first element in the
                if (verbose):
                    print("k:", k, "node:", v)

                if setlb[v]:

                    start_neighborhood_call = time()
                    len_nbr_v = H.get_number_of_nbrs(v)
                    self.neighborhood_call_time += time() - start_neighborhood_call
                    self.num_neighborhood_computation += 1

                    if len_nbr_v < k:
                        self.core[v] = k
                        setlb[v] = True

                        start_neighborhood_call = time()
                        nbr_v = H.neighbors(v)
                        self.neighborhood_call_time += time() - start_neighborhood_call
                        self.num_neighborhood_computation += 1

                        if (verbose):
                            print('removing ', v)
                        start_subgraph_time = time()
                        H.removeV_transform(v, verbose)  # Store.... + executation time..
                        # H.removeV_transform2(v, verbose)
                        self.subgraph_time += time() - start_subgraph_time
                        self.num_subgraph_call += 1
                        if (verbose):
                            print('nbrs: ', nbr_v)
                        for u in nbr_v:
                            self.total_iteration += 1
                            if not setlb[u]:
                                self.inner_iteration += 1
                                start_neighborhood_call = time()
                                len_neighbors_u = H.get_number_of_nbrs(u)
                                self.neighborhood_call_time += time() - start_neighborhood_call
                                self.num_neighborhood_computation += 1

                                max_value = max(len_neighbors_u, k)
                                if (verbose):
                                    print("max core between", k, 'and', len_neighbors_u, "is ", max_value)
                                    print("The location of", u, "is updated from", inverse_bucket[u], "to",
                                        max_value)

                                start_bucket_update = time()
                                bucket[inverse_bucket[u]].remove(u)

                                if max_value not in bucket:
                                    bucket[max_value] = set()
                                bucket[max_value].add(u)
                                self.num_bucket_update += 1
                                self.bucket_update_time += time() - start_bucket_update

                                # update new location of u
                                inverse_bucket[u] = max_value
                            
                    else:
                        start_bucket_update = time()
                        if len_nbr_v not in bucket:
                            bucket[len_nbr_v] = set()
                        bucket[len_nbr_v].add(v)
                        self.num_bucket_update += 1
                        self.bucket_update_time += time() - start_bucket_update

                        # update new location of u
                        inverse_bucket[v] = len_nbr_v
                        setlb[v] = False
                else:
                    self.core[v] = k
                    setlb[v] = True

                    start_neighborhood_call = time()
                    nbr_v = H.neighbors(v)
                    self.neighborhood_call_time += time() - start_neighborhood_call
                    self.num_neighborhood_computation += 1
                    if (verbose):
                        print('removing ', v)
                    start_subgraph_time = time()
                    H.removeV_transform(v, verbose)  # Store.... + executation time..
                    # H.removeV_transform2(v, verbose)
                    self.subgraph_time += time() - start_subgraph_time
                    self.num_subgraph_call += 1
                    if (verbose):
                        print('nbrs: ', nbr_v)
                    for u in nbr_v:
                        self.total_iteration += 1
                        if not setlb[u]:
                            self.inner_iteration += 1
                            start_neighborhood_call = time()
                            len_neighbors_u = H.get_number_of_nbrs(u)
                            self.neighborhood_call_time += time() - start_neighborhood_call
                            self.num_neighborhood_computation += 1

                            max_value = max(len_neighbors_u, k)
                            if (verbose):
                                print("max core between", k, 'and', len_neighbors_u, "is ", max_value)
                                print("The location of", u, "is updated from", inverse_bucket[u], "to",
                                    max_value)

                            start_bucket_update = time()
                            bucket[inverse_bucket[u]].remove(u)

                            if max_value not in bucket:
                                bucket[max_value] = set()
                            bucket[max_value].add(u)
                            self.num_bucket_update += 1
                            self.bucket_update_time += time() - start_bucket_update

                            # update new location of u
                            inverse_bucket[u] = max_value

                            if (verbose):
                                print("-------- Updated bucket ---------")
                                print(bucket)
                                print()

        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time

        if (verbose):
            print("\n\nOutput")
            print(self.core)

    def improvedNBR_simplified(self, H, verbose=True):
        # print(""" Bishwa simplified the correct version (improvedNBR()) by optimizing if-else conditions .  """)
        # This version also adopts Arijits simplification to Bishwa's simplification.
        start_execution_time = time()
        bucket = {}
        lb1 = H.glb
        ub1 = H.gub
        inverse_bucket = {}
        setlb = {}
        # Initial bucket fill-up
        start_init_time = time()
        for node in H.init_node_iterator():
            # lb = max(H.llb[node],lb1)
            lb = H.llb[node]

            inverse_bucket[node] = lb

            if lb not in bucket:
                bucket[lb] = set()
            bucket[lb].add(node)
            setlb[node] = True

        self.init_time = time() - start_init_time

        if (verbose):
            print("\n---------- Initial neighbors -------")
            # for node in H.nodes():
            #     print(node, H.neighbors(node))
            # print()

            print("\n---------- Initial bucket -------")
            print(bucket)
            print()

        start_loop_time = time()

        for k in range(lb1, ub1 + 1):
            while len(bucket.get(k, [])) != 0:
                v = bucket[k].pop()  # get first element in the
                if (verbose):
                    print("k:", k, "node:", v, ' setlb[v]: ',setlb[v])
                len_nbr_v = H.get_number_of_nbrs(v)
                # if setlb[v] and len_nbr_v >= k:
                if setlb[v]:
                    len_nbr_v = max(len_nbr_v,k)
                    if len_nbr_v not in bucket:
                        bucket[len_nbr_v] = set()
                    bucket[len_nbr_v].add(v)

                    # update new location of u
                    inverse_bucket[v] = len_nbr_v
                    setlb[v] = False
                else:
                    # print('assigning core: ',v)
                    self.core[v] = k
                    # setlb[v] = True

                    nbr_v = H.neighbors(v)
                    if (verbose):
                        print('removing ', v)
                    start_subgraph_time = time()
                    H.removeV_transform(v, verbose)  # Store.... + executation time..
                    # H.removeV_transform2(v, verbose)
                    self.subgraph_time += time() - start_subgraph_time
                    self.num_subgraph_call += 1
                    if (verbose):
                        print('nbrs: ', nbr_v)
                    for u in nbr_v:
                        self.total_iteration += 1
                        if not setlb[u]:
                            # print('updating neighbor(v)', u)
                            self.inner_iteration += 1
                            start_neighborhood_call = time()
                            len_neighbors_u = H.get_number_of_nbrs(u)
                            self.neighborhood_call_time += time() - start_neighborhood_call
                            self.num_neighborhood_computation += 1

                            max_value = max(len_neighbors_u, k)
                            if (verbose):
                                print("max core between", k, 'and', len_neighbors_u, "is ", max_value)
                                print("The location of", u, "is updated from", inverse_bucket[u], "to",
                                      max_value)

                            start_bucket_update = time()
                            bucket[inverse_bucket[u]].remove(u)

                            if max_value not in bucket:
                                bucket[max_value] = set()
                            bucket[max_value].add(u)
                            self.num_bucket_update += 1
                            self.bucket_update_time += time() - start_bucket_update

                            # update new location of u
                            inverse_bucket[u] = max_value

                            if (verbose):
                                print("-------- Updated bucket ---------")
                                print(bucket)
                                print()

        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time

        if (verbose):
            print("\n\nOutput")
            print(self.core)

    def improved2NBR(self, H, s = 1, verbose = True):
        """ 
        This is our original top-down, UB-based algorithm.
        :param H -> Hypergraph
        :param s -> Integer, algorithm parameter. 
        """
        start_execution_time = time()
        # num_nodes = 0
        # nodes = set()

        # glb = H.glb
        llb = H.llb
        # gub = H.gub
        lub = H.lub

        start_init_time = time()
        # Initial bucket fill-up
        # for node in H.init_node_iterator():
            # len_neighbors = H.get_init_nbrlen(node)
            # llb[node] = H.precomputedlb2[node]
            # lub[node] = H.precomputedub2[node]
            # self._node_to_num_neighbors[node] = len_neighbors
            
            # if len_neighbors not in bucket:
            #     bucket[len_neighbors] = set()
            # bucket[len_neighbors].add(node)
            # num_nodes += 1
            # nodes.add(node)

        if(verbose):
            pass
            # print("\n---------- Initial neighbors -------")
            # for node in H.nodes():
            #     print(node, H.neighbors(node))
            # print()

            # print("\n---------- Initial bucket -------")
            # print(bucket)
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

            V_kmin = [u for u in H.init_node_iterator() if lub[u] >= lower]
            if(verbose):
                print("Vkmin: ", V_kmin)
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
                            if not setlb[u]:
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

        V_kmin = [u for u in H.init_node_iterator() if H.precomputedub2[u] >= lower]
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

        # V_kmin = [u for u in H.init_node_iterator() if H.precomputedub2[u] >= lower]
        V_kmin = [u for u in H_kmin.init_node_iterator() if (lower <= H_kmin.precomputedub2[u] <= upper)]

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
        This is our original top-down, UB-based algorithms parallelized into threads. (Does not give correct core-numbers)
        :param H -> Hypergraph
        :param s -> Integer, algorithm parameter.
        """
        start_execution_time = time()

        # num_nodes = 0
        # nodes = set()

        # glb = H.glb
        llb = H.llb
        # gub = H.gub
        lub = H.lub

        start_init_time = time()
       
        # for node in H.init_node_iterator():
           
            # len_neighbors = H.get_init_nbrlen(node)
            
            # llb[node] = H.precomputedlb2[node]
            # lub[node] = H.precomputedub2[node]
            
            # self._node_to_num_neighbors[node] = len_neighbors
            
            # if len_neighbors not in bucket:
            #     bucket[len_neighbors] = set()
            # bucket[len_neighbors].add(node)
            # num_nodes += 1
            # nodes.add(node)

        if(verbose):
            pass
            # print("\n---------- Initial neighbors -------")
            # for node in H.nodes():
            #     print(node, H.neighbors(node))
            # print()

            # print("\n---------- Initial bucket -------")
            # print(bucket)
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
        This is our original top-down, UB-based algorithms parallelized into threads. (Does not give correct core-numbers).
        Unlike parallel_improved2NBR() this algorithm does not compute strong subhypergraph, rather each thread work on copies of the 
        original hypergraph.
        :param H -> Hypergraph
        :param s -> Integer, algorithm parameter.
        """
        start_execution_time = time()

        # num_nodes = 0
        # nodes = set()

        # glb = H.glb
        llb = H.llb
        # gub = H.gub
        lub = H.lub

        start_init_time = time()
        # Initial bucket fill-up
        # for node in H.init_node_iterator():
           
            # len_neighbors = H.get_init_nbrlen(node)
            
            # llb[node] = H.precomputedlb2[node]
            # lub[node] = H.precomputedub2[node]
            
            # self._node_to_num_neighbors[node] = len_neighbors
            
            # if len_neighbors not in bucket:
            #     bucket[len_neighbors] = set()
            # bucket[len_neighbors].add(node)
            # num_nodes += 1
            # nodes.add(node)

        if(verbose):
            pass
            # print("\n---------- Initial neighbors -------")
            # for node in H.nodes():
            #     print(node, H.neighbors(node))
            # print()

            # print("\n---------- Initial bucket -------")
            # print(bucket)
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

    def par_core_correct(self, args):
        """ 
        Verify if core_u locally satisfies the property that the induced sub_neighborhood of u has at least u vertices. 
        If true returns core_u, If False, returns the correctd core_value.
        """
        H, u, core_u, core_dict = args
        nbrhood_u_plus = set() # Contains the union of e \in incident_edge(u) such that every v \in e has core(v) >= core(u).
        
        # start_subgraph_time = time()
        for e_id in H.inc_dict[u]:
            edge = H.get_edge_byindex(e_id)
            flag = True
            for v in edge: 
                if u!=v:
                    if core_dict[v] < core_u: # If some vertex has core value < core_u ignore the whole hyperedge.
                        flag = False
                        break

            if flag:
                nbrhood_u_plus = nbrhood_u_plus.union(edge)
                nbrhood_u_plus.remove(u)

        # self.subgraph_time = time() - start_subgraph_time 
        if len(nbrhood_u_plus) >= core_u: # union of incident_edge(u) such that ... has at least core_u members. 
            # core_u locally satisfies coreness property, and the set nbr_u_plus certifies that. 
            return (u, True, core_u)
        else:
            # Does not locally satisfy the coreness property, decrease it by 1 and check if core_u - 1 satisfies it.
            core_u = core_u - 1
            return (u, False, self.core_correct(H, u, core_u, core_dict)[1])

    def par_local_core(self, H, num_threads = 4, verbose = True):
        start_execution_time = time()
        # Init
        start_init_time = time()
        for node in H.init_node_iterator():
            len_neighbors = H.get_init_nbrlen(node)
            self.core[node] = len_neighbors
            # num_nodes += 1
        self.init_time = time() - start_init_time  
        
        k = 0
        start_loop_time = time()
        while True:
            if (verbose):
                print("Iteration: ", k)
            flag = True

            start_inner_time = time()
            with Pool(num_threads) as p:
                return_values = p.map(par_operator_H, [ (node, [self.core[j] for j in H.get_init_nbr(node)]) for node in H.init_node_iterator()])

            # Retrieving return values
            for node, val in return_values:
                H_value = val
                if H_value <= self.core[node]:
                    self.core[node] = H_value
            self.inner_iteration = time() - start_inner_time

            start_core_correct_time = time()
            with Pool(num_threads) as p:
                return_values = p.map(self.par_core_correct, [ (H, node, self.core[node], self.core) for node in H.init_node_iterator()])
            # Retrieving return values
            for node, local_sat, val in return_values:
                self.core[node] = val
                if local_sat is False:
                    flag = False

            self.core_correct_time = time() - start_core_correct_time
            k+=1
            if flag:
                break
        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time

    def wrong_local_core(self, H, verbose = True):
        if verbose:
            print('tau: ', H.get_M())

        for node in H.init_node_iterator():
            len_neighbors = H.get_init_nbrlen(node)
            self.core[node] = len_neighbors
        
        if(verbose):
            print("Init core")
            print(self.core)

        # Main loop

        k = 0
        while k < 10:
            if (verbose):
                print("Iteration: ", k)

            temp = {}
            for node in H.init_node_iterator():
                temp[node] = operator_H([self.core[j] for j in H.get_init_nbr(node)])
                
            for node in H.init_node_iterator():
                self.core[node] = temp[node]
    
            if(verbose):
                print(self.core)

            k+=1

    def improved_local_core_rev(self, H, verbose = True):
        """ Not an improvement really!! 
        Vertices popped in Decreasing order of hindex from heap .
        """
        if verbose:
            print('tau: ', H.get_M())

        start_execution_time = time()
        # num_nodes = 0
        # Init
        start_init_time = time()
        dirty = heapdict()
        for node in H.init_node_iterator():
            len_neighbors = H.get_init_nbrlen(node)
            self.core[node] = len_neighbors
            dirty[node] = -len_neighbors
            # num_nodes += 1
        self.init_time = time() - start_init_time  
        if(verbose):
            print("Init core")
            print(self.core)

        # Main loop
        start_loop_time = time()
    
        k = 0
        
        while True:
            # print(k)
            if (verbose):
                print("Iteration: ", k)
            flag = True
            start_inner_time = time()
            for node in H.init_node_iterator():
                H_value = operator_H([self.core[j] for j in H.get_init_nbr(node)])
                self.core[node] = min(H_value, self.core[node])
                dirty[node] = -self.core[node]
                # else:
                #     if node in dirty:
                #         dirty.remove(node)
            # print(dirty)
            self.h_index_time += (time() - start_inner_time)
                # if(verbose):
                #     print("k:", k, "node:", node, "c[]=",self.core[node])
            
            start_core_correct_time = time()
            dirty2 = heapdict()
            while len(dirty):
                node, prev_core = dirty.popitem()
                if not self.LLCSAT(H, node, self.core[node], self.core):   
                    flag = False
                    self.core[node] = self.iterative_core_correct(H, node, self.core[node], self.core)
                    dirty2[node] = self.core[node]
                    # for u in H.init_nbr[node]:
                    #     LLCSAT_u = self.LLCSAT(H, u, self.core[u], self.core)
                    #     if not LLCSAT_u:
                    #         dirty2[u] = self.core[node]
                else:
                    dirty2[node] = prev_core
            dirty = dirty2
            # print('->',dirty)
            # core_corrected_bucket = set()
            # for node in H.init_node_iterator():
            #     if node not in core_corrected_bucket:          
            #         if not self.LLCSAT(H, node, self.core[node], self.core):   
            #             prev_core = self.core[node] 
            #             flag = False
            #             self.core[node] = self.iterative_core_correct(H, node, self.core[node], self.core)
            #             core_corrected_bucket.add(node)
                    
            #             for u in H.init_nbr[node]:
            #                 if self.core[u] > self.core[node] and self.core[u] <= prev_core: 
            #                     # Instead of checking LLCSAT again assume they must be corrected.
            #                     self.core[node] = self.iterative_core_correct(H, u, self.core[u], self.core)
            #                     core_corrected_bucket.add(u)
            self.core_correct_time += (time() - start_core_correct_time)
            k+=1
            if flag:
                break

        self.loop_time = time() - start_loop_time
        self.execution_time = time() - start_execution_time
        print(k)
        self.max_n = k
        # if(verbose):
        #     print(self.core)
