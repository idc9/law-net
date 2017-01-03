import glob
import numpy as np
import random as random
import pandas as pd
from math import *
from datetime import datetime

from experiment_helper_functions import *
from pipeline_helper_functions import *
from attachment_model_inference import *


def get_rankscores_search(G, test_params, metrics, subnet_dir, num_to_keep):
    """
    Computes rank scores for each metric individually in metrics list
    """

    # sample test cases
    test_cases = get_test_cases(G,
                                test_params['active_years'],
                                test_params['num_test_cases'],
                                test_params['seed'])

    # load snapshots
    snapshots_dict = load_snapshots(subnet_dir)

    # load tfidf matrix
    tfidf_matrix, op_id_to_bow_id = load_tf_idf(subnet_dir + 'nlp/')

    # ranking scores for each test case
    scores = pd.DataFrame(index=[c['name'] for c in test_cases],
                          columns=metrics)

    # get scores for each metric
    for metric in metrics:
        # compute scores on test cases
        scores[metric] = get_test_case_scores_search(G, test_cases, snapshots_dict,
                                                    metric, tfidf_matrix, op_id_to_bow_id, num_to_keep)

    return scores


def get_test_case_scores_search(G, test_cases, snapshots_dict, metric,
                                tfidf_matrix, op_id_to_bow_id, num_to_keep):
    """
    computes the scores for each test case

    returns a pandas series indexed by test case clids

    # TODO: this could be parallelized

    """
    # compute scores for each test case
    scores = pd.Series(index=[c['name'] for c in test_cases])
    for test_case in test_cases:
        scores[test_case['name']] = get_rankscore_search(G, test_case,
                                                         snapshots_dict,
                                                         metric, tfidf_matrix,
                                                         op_id_to_bow_id,
                                                         num_to_keep)

    return scores


def get_rankscore_search(G, test_case, snapshots_dict, metric,
                         tfidf_matrix, op_id_to_bow_id, num_to_keep):
    """
    Gets the rank score for a given test case
    """

    # converted ig index to CL id
    cited_cases = get_cited_cases(G, test_case)

    # get vetex metrics in year before citing year
    snapshot_year = test_case['year'] - 1

    # grab data frame of vertex metrics for test case's snapshot
    snapshot_df = snapshots_dict['vertex_metrics_' +
                                 str(int(snapshot_year))]

    # restrict ourselves to ancestors of ing
    # case strictly before ing year
    ancentors = [v.index for v in G.vs.select(year_le=snapshot_year)]

    # all edges from ing case to previous cases
    edgelist = zip([test_case.index] * len(ancentors), ancentors)

    columns_to_use = [metric, 'similarity']

    # grab edge data
    edge_data = get_edge_data(G, edgelist, snapshot_df, columns_to_use=columns_to_use,
                              tfidf_matrix=tfidf_matrix, op_id_to_bow_id=op_id_to_bow_id,
                              metric_normalization=None, edge_status=None)

    edge_data.sort_values(by='similarity', ascending=False).iloc[0:num_to_keep]

    # case rankings (CL ids)
    ancestor_ranking = rank_cases_by_metric(edge_data, metric)

    # compute rank score
    score = score_ranking(cited_cases, ancestor_ranking)

    return score
