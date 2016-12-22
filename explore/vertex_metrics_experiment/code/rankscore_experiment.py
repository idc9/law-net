import glob
import numpy as np
import random as random
import pandas as pd
from math import *
from datetime import datetime

from compute_ranking_metrics import *
from pipeline_helper_functions import *
from similarity_matrix import *
from attachment_model_inference import *


def get_all_individual_rankscores_LR(G, test_params, metrics,
                                     include_similarity, experiment_data_dir,
                                     print_progress=True):
    """
    Computes rank scores for each metric individually in metrics list
    """

    # sample test cases
    test_cases = get_test_cases(G,
                                test_params['active_years'],
                                test_params['num_test_cases'],
                                test_params['seed'])

    # load snapshots
    snapshots_dict = load_snapshots(experiment_data_dir)

    # mabye load the similarities
    if include_similarity:
        similarity_matrix, CLid_to_index = load_similarity_matrix(experiment_data_dir)
    else:
        similarity_matrix = None
        CLid_to_index = None

    # load edge data for all edges
    all_edge_data = pd.read_csv(experiment_data_dir + 'edge_data.csv',
                                index_col=0)

    # ranking scores for each test case
    scores = pd.DataFrame(index=[c['name'] for c in test_cases],
                          columns=metrics)

    # get scores for each metric
    for metric in metrics:

        if print_progress:
            print metric

        # either all metrics or individual metric
        if metric == 'all':
            columns_to_use = metrics
        else:
            columns_to_use = [metric]

        # wether or not to include similarity in the logistic regression
        if include_similarity and metric != 'similarity':
            columns_to_use.append('similarity')

        # fit logistic regression
        LogReg = fit_logistic_regression(all_edge_data, columns_to_use)

        # compute scores on test cases
        testcase_scores = get_test_case_scores_LR(G, test_cases, snapshots_dict,
                                                  similarity_matrix, CLid_to_index,
                                                  LogReg, columns_to_use, print_progress)

        scores[metric] = testcase_scores

    return scores


def get_single_rankscores_LR(G,
                             LogReg,
                             test_cases,
                             columns_to_use,
                             experiment_data_dir,
                             print_progress=False):
    '''
    Computes the rank score metric for a given logistic regression object.

    Sample R test cases that have at least one citation. For each test case
    rank test case's ancestors then compute rank score for test cases actual
    citations.

    Parameters
    ------------
    G: network (so we can get each cases' ancestor network)

    LogReg: a logistic regression object
    (i.e. the output of fit_logistic_regression)

    columns_to_use: list of column names of edge metrics data frame that we
    should use to fit logistic regression

    path_to_vertex_metrics_folder: we will need these for prediciton

    year_interval: the year interval between each vertex metric .csv file

    R: how many cases to compute ranking metrics for

    year_floor: sample only cases after this year

    seed: random seed for selecting cases whose ancsetry to score

    Output
    -------
    The average ranking score over all R cases we tested
    '''

    # ranking scores for each test case
    scores = pd.Series(index=[c['name'] for c in test_cases])

    # load snapshots
    snapshots_dict = load_snapshots(experiment_data_dir)

    # mabye load the similarities
    if 'similarity' in columns_to_use:
        similarity_matrix, CLid_to_index = load_similarity_matrix(experiment_data_dir)
    else:
        similarity_matrix = None
        CLid_to_index = None

    # run until we get R test cases (some cases might not have any citations)
    i = 0
    for test_case in test_cases:
        i += 1
        if print_progress:
            if int(log(i, 2)) == log(i, 2):
                current_time = datetime.now().strftime('%H:%M:%S')
                print '(%d/%d) at %s' % (i, R, current_time)

        score = get_score_LR(G, test_case, snapshots_dict, similarity_matrix,
                             CLid_to_index, LogReg, columns_to_use)

        scores[test_case['name']] = score

    return scores
