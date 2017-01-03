import glob
import numpy as np
import random as random
import pandas as pd
from math import *
from datetime import datetime

from experiment_helper_functions import *
from pipeline_helper_functions import *
from attachment_model_inference import *


def get_rankscores_sort(G, test_params, metrics,
                        subnet_dir):
    """
    Computes rank scores for each metric individually in metrics list
    """

    # sample test cases
    test_cases = get_test_cases(G,
                                test_params['active_years'],
                                test_params['num_test_cases'],
                                test_params['seed'])

    # load tfidf matrix
    tfidf_matrix, op_id_to_bow_id = load_tf_idf(subnet_dir + 'nlp/')

    # ranking scores for each test case
    scores = pd.DataFrame(index=[c['name'] for c in test_cases],
                          columns=metrics)

    # score each test case
    for test_case in test_cases:
        # converted ig index to CL id
        cited_cases = get_cited_cases(G, test_case)

        # grab data frame of vertex metrics for test case's snapshot
        snapshot_year = test_case['year'] - 1
        snap_path = subnet_dir + 'snapshots/vertex_metrics_' + str(int(snapshot_year)) + '.csv'
        snapshot_df = pd.read_csv(snap_path, index_col=0)

        # restrict ourselves to ancestors of ing
        # case strictly before ing year
        ancentors = [v.index for v in G.vs.select(year_le=snapshot_year)]

        # all edges from ing case to previous cases
        edgelist = zip([test_case.index] * len(ancentors), ancentors)

        # grab edge data
        edge_data = get_edge_data(G, edgelist, snapshot_df, columns_to_use=metrics,
                                  tfidf_matrix=tfidf_matrix, op_id_to_bow_id=op_id_to_bow_id,
                                  metric_normalization=None, edge_status=None)

        # score each metric
        for metric in metrics:
            # case rankings (CL ids)
            ancestor_ranking = rank_cases_by_metric(edge_data, metric)

            # compute rank score
            scores.loc[test_case['name'], metric] = score_ranking(cited_cases,
                                                                  ancestor_ranking)

    return scores
