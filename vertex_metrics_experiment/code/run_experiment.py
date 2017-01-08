import sys
import numpy as np
import igraph as ig
import time

# repo_directory = '/nas/longleaf/home/idcarm/projects/law-net/'
# data_dir = '/nas/longleaf/home/idcarm/data/courtlistener/'

repo_directory = '/Users/iaincarmichael/Dropbox/Research/law/law-net'
data_dir = '/Users/iaincarmichael/data/courtlistener/'


# sys.path.append(repo_directory + 'vertex_metrics_experiment/code/')
from experiment_helper_functions import get_test_cases
from run_exper_functions import *




def get_vertex_metrics():
    if network_name == 'scotus':
        
        vertex_metrics = ['indegree', 'outdegree', 'degree',
                          'd_pagerank', 'u_pagerank',
                          'authorities', 'hubs',
                          #'d_eigen', 'u_eigen', # d_eigen is being problematic
                          'u_eigen',
                          'd_betweenness', 'u_betweenness',
                          'd_closeness', 'u_closeness']

        # add recent citations
        vertex_metrics += ['recentcite_' + str(t) for t in np.arange(1, 10 + 1)]
        vertex_metrics += ['recentcite_' + str(t) for t in [15, 20, 25, 30, 35, 40]]
        vertex_metrics += ['age', 'similarity']

    else:
        vertex_metrics = ['indegree', 'outdegree', 'degree',
                          'd_pagerank','u_pagerank',
                          'authorities', 'hubs',
                           #'d_eigen', 'u_eigen', # d_eigen is being problematic
                           'u_eigen']#,
                           #'d_betweenness', 'u_betweenness',
                           #'d_closeness', 'u_closeness']

        # add recent citations
        vertex_metrics += ['recentcite_' + str(t) for t in np.arange(1, 10 + 1)]
        vertex_metrics += ['recentcite_' + str(t) for t in [15, 20, 25, 30, 35, 40]]

        vertex_metrics += ['age', 'similarity']
        
        
        
    # # for testing
    # vertex_metrics = ['age', 'similarity']
    # vertex_metrics += ['indegree', 'outdegree']

    return vertex_metrics


def get_testcase_ids(G, active_years):
    # test cases
    test_seed = 2452,
    num_test_cases = 1000
    test_cases = get_test_cases(G, active_years,
                                num_test_cases, seed=test_seed)
    test_case_ids = [v.index for v in test_cases]

    return test_case_ids


def main():    
                
    network_name = 'federal'
    to_run = ['sort']
    name = 'federal_test'
    
    # directory set up
    subnet_dir = data_dir + network_name + '/'
    results_dir = subnet_dir + 'results/'

    # load graph
    G = ig.Graph.Read_GraphML(subnet_dir + network_name + '_network.graphml')

    # set vertex metrics
    vertex_metrics = get_vertex_metrics(network_name)

    # active years
    active_years = range(1900, 2015 + 1)

    # test case ids
    test_case_ids = get_testcase_ids(G, active_years)

    if 'sort' in to_run:
        print 'starting sort'
        # run sort
        sort_params = {}
        exper_params_sort = {'vertex_metrics': vertex_metrics,
                             'active_years': active_years,
                             'test_case_ids': test_case_ids,
                             'sort_params': sort_params}

        start = time.time()
        run_sort(G, exper_params_sort, subnet_dir, name)
        print 'sort took %d seconds' % (time.time()- start)

    if 'match' in to_run():
        print 'starting match'
        # run match
        num_to_keep = 5000
        match_params = {'num_to_keep': num_to_keep}

        exper_params_match = {'vertex_metrics': vertex_metrics,
                              'active_years': active_years,
                              'test_case_ids': test_case_ids,
                              'match_params': match_params}

        start = time.time()
        run_match(G, exper_params_match, subnet_dir, name)
        print 'match took %d seconds' % (time.time() - start)

    if 'logreg' in to_run:
        print 'starting logreg'
        # run logreg
        num_absent_edges = len(G.es)
        seed_edge_df = 65432
        metric_normalization = 'mean'
        feature_transform = 'interaction'
        make_tr_data = False

        logreg_params = {'num_absent_edges': num_absent_edges,
                         'seed_edge_df': seed_edge_df,
                         'metric_normalization': metric_normalization,
                         'feature_transform': feature_transform,
                         'make_tr_data': make_tr_data}

        exper_params_logreg = {'vertex_metrics': vertex_metrics,
                               'active_years': active_years,
                               'test_case_ids': test_case_ids,
                               'logreg_params': logreg_params}

        start = time.time()
        run_logreg(G, exper_params_logreg, subnet_dir, name)
        print 'logreg took %d seconds' % (time.time() - start)

if __name__ == '__main__':
    main()
