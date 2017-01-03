import glob
import numpy as np
import random as random
import pandas as pd
from math import *
from datetime import datetime
import copy

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

    # load tfidf matrix
    tfidf_matrix, op_id_to_bow_id = load_tf_idf(subnet_dir + 'nlp/')

    # ranking scores for each test case
    scores = pd.DataFrame(index=[c['name'] for c in test_cases],
                          columns=metrics)

    # columns for edge data
    columns_to_use = copy.copy(metrics)
    columns_to_use.append('similarity')

    # score each test case
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
        searched_cases = [e.split('_')[1] for e in edge_data.index]
        # [e[1] for e in sored_edges]
        searched_cases_cited = set(cited_cases).intersection(set(searched_cases))

        # if non of the cited cases are in the "searched cases" then keep
        # score is nan
        if len(searched_cases_cited) > 0:
            for metric in metrics:
                # case rankings (CL ids)
                ancestor_ranking = rank_cases_by_metric(edge_data, metric)
                scores.loc[test_case['name'], metric] = score_ranking(searched_cases_cited, ancestor_ranking)

    return scores
