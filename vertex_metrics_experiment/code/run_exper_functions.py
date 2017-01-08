import os
import cPickle as pickle

from rankscore_experiment_sort import get_rankscores_sort
from rankscore_experiment_match import get_rankscores_match
from rankscore_experiment_LR import get_rankscores_LR
from make_tr_edge_df import make_tr_edge_df

import datetime


def run_sort(G, exper_params, subnet_dir, name=None):

    # create results directory
    if name is None:
        name = get_datestamp()
    results_dir = subnet_dir + 'results/sort/%s/' % name
    os.makedirs(results_dir)

    # load exper params
    vertex_metrics = exper_params['vertex_metrics']
    active_years = exper_params['active_years']
    test_case_ids = exper_params['test_case_ids']
    sort_params = exper_params['sort_params']

    # grab test cases vertices
    test_cases = [G.vs[op_id] for op_id in test_case_ids]
    rankloss_sort = get_rankscores_sort(G, test_cases, vertex_metrics, subnet_dir)

    with open(results_dir + 'rankloss_sort.p', 'wb') as fp:
        pickle.dump(rankloss_sort, fp)

    with open(results_dir + 'exper_params_sort.p', 'wb') as fp:
        pickle.dump(exper_params, fp)


def run_match(G, exper_params, subnet_dir, name=None):
    # create results directory
    if name is None:
        name = get_datestamp()
    results_dir = subnet_dir + 'results/match/%s/' % name
    os.makedirs(results_dir)

    # load exper params
    vertex_metrics = exper_params['vertex_metrics']
    active_years = exper_params['active_years']
    test_case_ids = exper_params['test_case_ids']
    match_params = exper_params['match_params']

    # grab test cases vertices
    test_cases = [G.vs[op_id] for op_id in test_case_ids]
    num_to_keep = match_params['num_to_keep']
    rankloss_match = get_rankscores_match(G, test_cases, vertex_metrics, subnet_dir, num_to_keep)

    with open(results_dir + 'rankloss_match.p', 'wb') as fp:
        pickle.dump(rankloss_match, fp)

    with open(results_dir + 'exper_params_match.p', 'wb') as fp:
        pickle.dump(exper_params, fp)


def run_logreg(G, exper_params, subnet_dir, name=None):

    # create results directory
    if name is None:
        name = get_datestamp()
    results_dir = subnet_dir + 'results/logreg/%s/' % name
    os.makedirs(results_dir)

    # load exper params
    vertex_metrics = exper_params['vertex_metrics']
    active_years = exper_params['active_years']
    test_case_ids = exper_params['test_case_ids']
    logreg_params = exper_params['logreg_params']

    metric_normalization = logreg_params['metric_normalization']
    feature_transform = logreg_params['feature_transform']

    # maybe make training data frame
    if logreg_params['make_tr_data']:

        num_absent_edges = logreg_params['num_absent_edges']
        seed_edge_df = logreg_params['seed_edge_df']

        make_tr_edge_df(G, subnet_dir,
                        active_years, num_absent_edges,
                        vertex_metrics, metric_normalization,
                        seed=seed_edge_df)

    # grab test cases vertices
    test_cases = [G.vs[op_id] for op_id in test_case_ids]
    rankloss_LR, LogRegs = get_rankscores_LR(G, test_cases, vertex_metrics, subnet_dir,
                                             metric_normalization, feature_transform)

    with open(results_dir + 'rankloss_LR.p', 'wb') as fp:
        pickle.dump(rankloss_LR, fp)

    with open(results_dir + 'LogRegs.p', 'wb') as fp:
        pickle.dump(LogRegs, fp)

    with open(results_dir + 'exper_params_logreg.p', 'wb') as fp:
        pickle.dump(exper_params, fp)


def get_datestamp():
    date = datetime.datetime.now()
    stamp = "%s-%s-%s" % (date.month, date.day, date.year, date.hour, date.minute)
    return stamp


def setup_results_dir(subnet_dir):
    results_dir = subnet_dir + 'results/'

    paths = [results_dir, results_dir + 'sort/', results_dir + 'match/',
             results_dir + 'logreg/']

    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)
