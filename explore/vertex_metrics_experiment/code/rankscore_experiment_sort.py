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


def get_rankscores_sort(G, test_params, metrics,
                        experiment_data_dir,
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

    # ranking scores for each test case
    scores = pd.DataFrame(index=[c['name'] for c in test_cases],
                          columns=metrics)

    # get scores for each metric
    for metric in metrics:

        if print_progress:
            print metric

        # compute scores on test cases
        testcase_scores = get_test_case_scores_sort(G, test_cases, snapshots_dict, metric, print_progress=False)

        scores[metric] = testcase_scores

    return scores


def get_test_case_scores_sort(G, test_cases, snapshots_dict, metric, print_progress=False):
    """
    computes the scores for each test case

    returns a pandas series indexed by test case clids

    # TODO: this could be parallelized

    """
    # compute scores for each test case
    scores = pd.Series(index=[c['name'] for c in test_cases])
    i = 0
    for test_case in test_cases:
        i += 1
        if print_progress:
            if int(log(i, 2)) == log(i, 2):
                current_time = datetime.now().strftime('%H:%M:%S')
                print '(%d/%d) at %s' % (i, len(test_cases), current_time)

        score = get_score_sort(G, test_case, snapshots_dict, metric)

        scores[test_case['name']] = score

    return scores


def get_score_sort(G, test_case, snapshots_dict, metric):
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

    # grab edge data
    edge_data = get_edge_data(G, edgelist, snapshot_df, columns_to_use=metric,
                              tfidf_matrix=None, op_id_to_bow_id=None,
                              metric_normalization=None, edge_status=None)

    # case rankings (CL ids)
    edge_data['rand'] = np.random.uniform(size=edge_data.shape[0])
    ancestor_ranking = get_case_ranking_by_metric(edge_data, metric='rand')

    # compute rank score
    score = score_ranking(cited_cases, ancestor_ranking)

    return score


def get_case_ranking_by_metric(edge_data, metric):
    """
    Sorts cases by a given metric
    Parameters
    ----------
    edge_data: edge data frame
    metric: a single column from edge_data
    Output
    ------
    CL ids of ranked cases
    """

    # larger value of metric is means more likely to be cited
    large_is_good = True
    ascending = (not large_is_good)

    # sort edges by metric
    sored_edges = edge_data.sort_values(by=metric,
                                        ascending=ascending).index.tolist()

    # return cited case
    return np.array([e.split('_')[1] for e in sored_edges])
