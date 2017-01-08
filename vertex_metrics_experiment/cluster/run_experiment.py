import sys
import numpy as np
import igraph as ig

#repo_directory = '/nas/longleaf/home/idcarm/projects/law-net/'
#data_dir = '/nas/longleaf/home/idcarm/data/courtlistener/'

repo_directory = '/Users/iaincarmichael/Dropbox/Research/law/law-net'
data_dir = '/Users/iaincarmichael/data/courtlistener/'


sys.path.append(repo_directory + 'vertex_metrics_experiment/code/')
# from experiment_helper_functions import get_test_cases
from code import experiment_helper_functions
from run_exper import *

network_name = 'scotus'
subnet_dir = data_dir + network_name + '/'
results_dir = subnet_dir + 'results/'


def get_vertex_metrics():
    # vertex_metrics = ['indegree', 'outdegree', 'degree',
    #                   'd_pagerank', 'u_pagerank',
    #                   'authorities', 'hubs',
    #                   #'d_eigen', 'u_eigen', # d_eigen is being problematic
    #                   'u_eigen',
    #                   'd_betweenness', 'u_betweenness',
    #                   'd_closeness', 'u_closeness']
    #
    # # add recent citations
    # vertex_metrics += ['recentcite_' + str(t) for t in np.arange(1, 10 + 1)]
    # vertex_metrics += ['recentcite_' + str(t) for t in [15, 20, 25, 30, 35, 40]]
    # vertex_metrics += ['age', 'similarity']

    # for testing
    vertex_metrics = ['age', 'similarity']
    vertex_metrics += ['indegree', 'outdegree']

    return vertex_metrics


def get_testcase_ids(G, active_years):
    # test cases
    test_seed = 4332,
    num_test_cases = 10
    test_cases = get_test_cases(G, active_years,
                                num_test_cases, seed=test_seed)
    test_case_ids = [v.index for v in test_cases]

    return test_case_ids


def main():
    name = 'test'

    # load graph
    G = ig.Graph.Read_GraphML(subnet_dir + network_name + '_network.graphml')

    # set vertex metrics
    vertex_metrics = get_vertex_metrics()

    # active years
    active_years = range(1900, 2015 + 1)

    # test case ids
    test_case_ids = get_testcase_ids(G, active_years)

    # run experiment sort
    sort_params = {}
    exper_params_sort = {'vertex_metrics': vertex_metrics,
                         'active_years': active_years,
                         'test_case_ids': test_case_ids,
                         'sort_params': sort_params}
    run_sort(G, exper_params_sort, subnet_dir, name)

if __name__ == '__main__':
    main()
