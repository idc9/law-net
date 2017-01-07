import glob
import numpy as np
import random as random
import pandas as pd
from math import *
from datetime import datetime

from experiment_helper_functions import *
from pipeline_helper_functions import *
from attachment_model_inference import *
from rank_loss_functions import *


def get_rankscores_sort(G, test_cases, metrics, subnet_dir):
    """
    Computes rank scores for each metric individually in metrics list
    """

    # load the tfidf matrix
    tfidf_matrix, op_id_to_bow_id = load_tf_idf(subnet_dir + 'nlp/')

    # ranking loss: mean rank score, reicprocal rank, precision at K
    MRS = pd.DataFrame(index=[c['name'] for c in test_cases], columns=metrics)
    RR = pd.DataFrame(index=[c['name'] for c in test_cases], columns=metrics)
    PAK100 = pd.DataFrame(index=[c['name'] for c in test_cases], columns=metrics)
    PAK1000 = pd.DataFrame(index=[c['name'] for c in test_cases], columns=metrics)

    # evalute each test case
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

        # evaluate each metric
        for metric in metrics:

            ranking = get_rank_by_metric(edge_data, metric)

            # ranking loss
            mrs = get_mean_rankscore(cited_cases, ranking)
            rr = get_reciprocal_rank(cited_cases, ranking)
            pak100 = get_precision_at_K(cited_cases, ranking, 100)
            pak1000 = get_precision_at_K(cited_cases, ranking, 1000)

            # update data frames
            MRS.loc[test_case['name'], metric] = mrs
            RR.loc[test_case['name'], metric] = rr
            PAK100.loc[test_case['name'], metric] = pak100
            PAK1000.loc[test_case['name'], metric] = pak1000

        ranking_loss = {'MRS': MRS,
                        'RR': RR,
                        'PAK100': PAK100,
                        'PAK1000': PAK1000}

    return ranking_loss
