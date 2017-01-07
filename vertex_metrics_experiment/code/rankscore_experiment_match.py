import glob
import numpy as np
import random as random
import pandas as pd
from math import *
from datetime import datetime
import copy

from experiment_helper_functions import *
from pipeline_helper_functions import *
from rank_loss_functions import *


def get_rankscores_match(G, test_cases, metrics, subnet_dir, num_to_keep):
    """
    Computes rank scores for each metric individually in metrics list

    Output
    ------
    ranking_loss: dict containing all ranking loss functions
    """

    # load the tfidf matrix
    tfidf_matrix, op_id_to_bow_id = load_tf_idf(subnet_dir + 'nlp/')

    # ranking loss: mean rank score, reicprocal rank, precision at K
    MRS = pd.DataFrame(index=[c['name'] for c in test_cases], columns=metrics)
    RR = pd.DataFrame(index=[c['name'] for c in test_cases], columns=metrics)
    PAK100 = pd.DataFrame(index=[c['name'] for c in test_cases], columns=metrics)
    PAK1000 = pd.DataFrame(index=[c['name'] for c in test_cases], columns=metrics)

    # columns for edge data
    columns_to_use = copy.copy(metrics)
    columns_to_use.append('similarity')

    # evalute each test case
    for test_case in test_cases:
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
        edge_data_ancestors = get_edge_data(G, edgelist, snapshot_df, columns_to_use=columns_to_use,
                                            tfidf_matrix=tfidf_matrix, op_id_to_bow_id=op_id_to_bow_id,
                                            metric_normalization=None, edge_status=None)

        # keep subset of similar cases
        edge_data = edge_data_ancestors.sort_values(by='similarity',
                                                    ascending=False).iloc[0:num_to_keep]

        # test case citations
        cited_cases = get_cited_cases(G, test_case)

        # cited cases that are apart of the 'search'
        searched_cases = [e[1] for e in edge_data.index]
        searched_cases_cited = set(cited_cases).intersection(set(searched_cases))

        # if non of the cited cases are in the "searched cases" then keep
        # score is nan
        if len(searched_cases_cited) > 0:
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
