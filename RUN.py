from copy import deepcopy
from operator import attrgetter
import sys, time


class Matching(object):
    id = 0
    def __init__(self, edges):
        self.id = Matching.id
        Matching.id += 1
        self.edges = edges
        self.weight = 0
        self.num_edges = 0
        for edge in self.edges:
            self.weight += edge.weight
    
    def add_edge(self, edge):
        self.edges.append(edge)
        self.weight += edge.weight
        self.num_edges += 1
    
    def __eq__(self, other):
        for edge in self.edges:
            
            if edge not in other.edges:
                return False
        
        return True
    
    def __lt__(self, other):
        self_list = []
        other_list = []
        for edge in self.edges:
            self_list.append((int(edge.u.node_id), int(edge.v.node_id)))
            
        for edge in other.edges:
            other_list.append((int(edge.u.node_id), int(edge.v.node_id)))
        return tuple(self_list) < tuple(other_list)
    
    def __str__(self):
        ret_str = ''
        prefix = ''
        for edge in self.edges:
            ret_str += prefix + '%s:%s' % (str(edge.u.node_id), str(edge.v.node_id))
            prefix = ' '
        return ret_str

class ConvexBipartiteGraph(object):
    def __init__(self, graph_id, tic_list, tac_list):
        self.id = graph_id
        # O(Nlog(N)), N = |U|
        self.tic_list = sorted(tic_list, reverse=True, key=attrgetter('weight'))
        # O(Mlog(M)), M = |V|
        self.tac_list = sorted(tac_list, key=attrgetter('node_id'))
        # O(M)
        self.tic_dict = {tic.node_id: tic for tic in self.tic_list}
        self.tac_dict = {tac.node_id : tac for tac in self.tac_list}
        
        self.edge_list = self.generate_edge_list()
        
        
    def generate_matchings(self, matchings, matching, edges, u, v):
        ''' take or leave strategy: O(2^(|E|)) 
        matchings: List of matchings
        matching: List of edges included in current matching
        edges: List of remaining edges
        u: dict of tics
        v: dict of tacs
        '''
        # because python passes by ref and these objects are mutable, we need deep copies
        matching = deepcopy(matching)
        edges = deepcopy(edges)
        u = deepcopy(u)
        v = deepcopy(v)
        # base case
        if not edges:
            matchings.append(matching)
            return matchings
        else:
            edge = edges.pop(0)
            
            # leave
            matchings = self.generate_matchings(matchings, matching, edges, u, v)
            
            if u[edge.u.node_id].free and v[edge.v.node_id].free:
                # take
                u[edge.u.node_id].free = False
                v[edge.v.node_id].free = False
                matching.add_edge(edge)
                matchings = self.generate_matchings(matchings, matching, edges, u, v)
        return matchings    
    
    def mark_all_free(self):
        for _, tic in self.tic_dict.iteritems():
            tic.free = True
        for _, tac in self.tac_dict.iteritems():
            tac.free = True
        
    def generate_edge_list(self):
        edge_list = []
        for tic in self.tic_list:
            tic.sort_tacs(self.tac_list)
            for tac in tic.sorted_tacs:
                edge_list.append(Edge(tic, tac))   
        return edge_list
        
    def __str__(self):
        ret_str = '===========GRAPH %s============\n' % self.id
        for tic in self.tic_list:
            ret_str += str(tic)
        for tac in self.tac_list:
            ret_str += str(tac)
            
        return ret_str

class Edge(object):
    id = 0
    def __init__(self, u, v):
        self.id = Edge.id
        Edge.id += 1
        self.u = u
        self.v = v
        self.weight = u.weight + v.weight
        
    def __str__(self):
        ret_str = '======EDGE %s========\n' % str(self.id) + str(self.u.node_id) + ',' + str(self.v.node_id) 
        ret_str += '\nWeight: ' + str(self.weight)
        return ret_str
    
    def __lt__(self, other):
        if self.v == other.v:
            return self.u < other.u
        else:
            return self.v < other.v
    
    def __eq__(self, other):
        return self.u.node_id == other.u.node_id and self.v.node_id == other.v.node_id
    
class Tic(object):
    def __init__(self, node_id, min_node, max_node, weight):
        self.node_id = int(node_id)
        self.min = int(min_node)
        self.max = int(max_node)
        self.weight = int(weight)
        self.sorted_tacs = None
        self.chosen_tac = None
        self.free = True
        
    def sort_tacs(self, tac_list):
        ''' time complexity MLog(M) where M = |V| '''
        available_tacs = []
        for tac in tac_list:
            if tac.node_id >= self.min and tac.node_id <= self.max:
                available_tacs.append(tac)
        self.sorted_tacs = sorted(available_tacs, key=attrgetter('weight'))
        
    def __str__(self):
        return '&&&&&&&&&&&&\nTIC\nID:%s\nMin:%s\nMax:%s\nWeight:%s\n' % \
            (str(self.node_id), str(self.min), str(self.max), str(self.weight))
            
    def __lt__ (self, other):
        if self.max == other.max:
            return self.min < other.min
        return self.max < other.max
    
class Tac(object):

    def __init__(self, node_id, weight):
        self.node_id = int(node_id)
        self.weight = int(weight)
        self.chosen_tic = None
        self.free = True
        
    def __str__(self):
        return '*********\nTAC\nID:%s\nWeight:%s\n' % (str(self.node_id), str(self.weight))
    
    def __lt__(self, other):
        return self.node_id < other.node_id
    
    def __ge__(self, other):
        return self.weight >= other.weight
    
def main(filename):
    #filename = 'Level0/input0.txt'
    print ('Reading from %s...' % filename)
    out_filename = filename.replace('.in', '.out')
    
    # read from file, generate objects
    f = open(filename, 'r')
    all_matchings = []
    num_graphs = int(f.readline())
    for j in range(num_graphs):
        tic_list = []
        tac_list = []
        #TODO why does this loop not work
        (num_tics, num_tacs) = f.readline().split()
        for _ in range(int(num_tics)):
            (node_id, node_min, node_max, weight) = f.readline().split()
            tic_list.append(Tic(node_id, node_min, node_max, weight))
        for _ in range(int(num_tacs)):
            (node_id, weight) = f.readline().split()
            tac_list.append(Tac(node_id, weight))
        graph = ConvexBipartiteGraph(j, tic_list, tac_list)
        start_time = time.time()
        print ('Done. Generating matchings for graph %s...' % str(j))
        # brute force all matchings - O(2^n)
        m = graph.generate_matchings([], Matching([]), graph.edge_list, graph.tic_dict, graph.tac_dict)
        
        # sort by number of edges, remove those with fewer than max
        # O(n2^n)
        m.sort(key=attrgetter('num_edges'), reverse=True)
        max_card = m[0].num_edges
        i = 0
        while i < len(m):
            if m[i].num_edges < max_card:
                m.pop(i)
            else:
                i+=1
        elapsed = time.time() - start_time
        print('Done after %s seconds. Sorting matchings for graph %s...' % (str(elapsed), str(j)))    
        # sort by weight, remove those with less than max weight
        m.sort(key=attrgetter('weight'), reverse=True)
        max_weight = m[0].weight
        i = 0
        while i < len(m):
            if m[i].weight < max_weight:
                m.pop(i)
            else:
                i+=1

        for matching in m:
            matching.edges.sort()
        m.sort()
        all_matchings.append(m)
    f.close()
    print ("Done. Writing output to %s..." % out_filename)
    # write output file
    f = open(out_filename, 'w+')
    for m in all_matchings:
        f.write(str(len(m)) + '\n')
        for matching in m:
            f.write(str(matching) + '\n')
    print ("Write complete.")

if __name__ == '__main__':
    # get argument from command line, generate output name
    filename = sys.argv[1]
    main(filename)

    
    
