import glob
import numpy as np
import random as random
import pandas as pd
from math import *
from datetime import datetime

from experiment_helper_functions import *
from pipeline_helper_functions import *
from attachment_model_inference import *
from bag_of_words import *


def get_rankscores_LR(G, test_params, metrics,
                      include_similarity, subnet_dir,
                      metric_normalization=None):
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

    # mabye load the similarities
    if include_similarity:
        tfidf_matrix, op_id_to_bow_id = load_tf_idf(subnet_dir + 'nlp/')
    else:
        tfidf_matrix = None
        op_id_to_bow_id = None

    # load edge data for all edges
    tr_edge_data = pd.read_csv(subnet_dir + 'edge_data.csv',
                               index_col=0)

    # ranking scores for each test case
    scores = pd.DataFrame(index=[c['name'] for c in test_cases],
                          columns=metrics)

    # get scores for each metric
    for metric in metrics:
        # either all metrics or individual metric
        if metric == 'all':
            columns_to_use = metrics
            columns_to_use.remove('all')
        else:
            columns_to_use = [metric]

        # wether or not to include similarity in the logistic regression
        if include_similarity and metric != 'similarity':
            columns_to_use.append('similarity')

        # fit logistic regression
        LogReg = fit_logistic_regression(tr_edge_data, columns_to_use)

        # compute scores on test cases
        testcase_scores = get_test_case_scores_LR(G, test_cases, snapshots_dict,
                                                  tfidf_matrix, op_id_to_bow_id,
                                                  LogReg, columns_to_use,
                                                  metric_normalization)

        scores[metric] = testcase_scores

    return scores


def get_test_case_scores_LR(G, test_cases, snapshots_dict,
                            tfidf_matrix, op_id_to_bow_id,
                            LogReg, columns_to_use, metric_normalization):
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

        score = get_score_LR(G, test_case, snapshots_dict,
                             tfidf_matrix, op_id_to_bow_id,
                             LogReg, columns_to_use, metric_normalization)

        scores[test_case['name']] = score

    return scores


def get_score_LR(G, test_case, snapshots_dict, tfidf_matrix, op_id_to_bow_id,
                 LogReg, columns_to_use, metric_normalization):
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
    edge_data = get_edge_data(G, edgelist, snapshot_df, columns_to_use,
                              tfidf_matrix, op_id_to_bow_id,
                              metric_normalization, edge_status=None)

    # case rankings (CL ids)
    ancestor_ranking = get_case_ranking_logreg(edge_data,
                                               LogReg,
                                               columns_to_use)

    # compute rank score
    score = score_ranking(cited_cases, ancestor_ranking)

    return score


def get_attachment_probabilty_logreg(LogReg, X):
    '''
    Evaluates our logistic regression model for a given dataset.

    Parameters
    ------------
    LogReg: a logistic regression object
    (i.e. the output of fit_logistic_regression)

    X: columns of vertex_df used in evaluating the
    logistical regression

    Output
    ------
    returns a list of df of attachment probabilities
    '''
    # TODO: double check we have classes right and order of X cols right

    # create probability data frame
    prob_df = pd.DataFrame(index=X.index)

    # which class??
    citation_index = np.where(LogReg.classes_ == 1)[0]
    prob_df['citation_prob'] = LogReg.predict_proba(X)[:, citation_index]  # should this be 0 or 1??

    return prob_df


def get_case_ranking_logreg(edge_data, LogReg, columns_to_use):
    """
    Ranks cases using provided logistic regression

    Paramters
    ---------
    edge_data: edge data data frame indexed by CLid edges

    LogReg: trained scikit learn logistic regression object

    columns_to_use: which columns to use to use for prediction

    Output
    ------
    numpy array of CLids in order of ranking
    """
    # probability a case is cited
    citation_probs = get_attachment_probabilty_logreg(LogReg,
                                                      edge_data[columns_to_use])

    # sort by attachment probabilities
    citation_probs.sort_values('citation_prob', ascending=False,
                               kind='mergesort', inplace=True)

    # case rankings (CL ids)
    # return np.array([e[1] for e in citation_probs.index])
    return np.array([e.split('_')[1] for e in citation_probs.index])
