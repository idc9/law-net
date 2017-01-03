import glob
import numpy as np
import random as random
import pandas as pd
from math import *
from datetime import datetime
import copy

from sklearn.metrics import log_loss
import scipy as sp

from experiment_helper_functions import *
from pipeline_helper_functions import *
from attachment_model_inference import *
from bag_of_words import *


def get_rankscores_LR(G, test_params, metrics, subnet_dir,
                      metric_normalization=None):
    """
    Computes rank scores for each metric individually in metrics list
    """

    # sample test cases
    test_cases = get_test_cases(G,
                                test_params['active_years'],
                                test_params['num_test_cases'],
                                test_params['seed'])

    # load the tfidf matrix
    tfidf_matrix, op_id_to_bow_id = load_tf_idf(subnet_dir + 'nlp/')

    # ranking scores for each test case
    rank_scores = pd.DataFrame(index=[c['name'] for c in test_cases],
                               columns=metrics)

    # ranking scores for each test case
    logloss_scores = pd.DataFrame(index=[c['name'] for c in test_cases],
                                  columns=metrics)

    # fit each logistic regression model
    LogRegs = fit_LogRegs(subnet_dir, metrics)

    # evaluate logistic regression on each test case
    for test_case in test_cases:
        # test case citations
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
        columns_to_use = copy.deepcopy(metrics)
        edge_data = get_edge_data(G, edgelist, snapshot_df,
                                  columns_to_use=metrics,
                                  tfidf_matrix=tfidf_matrix,
                                  op_id_to_bow_id=op_id_to_bow_id,
                                  metric_normalization=metric_normalization,
                                  edge_status=None)

        # evaluate each metric
        for metric in metrics:

            # get columns for logistic regression
            columns_to_use = get_columns(metrics, metric)

            # get prefitting logistic regressions
            LogReg = LogRegs[metric]

            # probability a case is cited
            citation_probs = get_attachment_probabilty_logreg(LogReg,
                                                              edge_data[columns_to_use])

            # sort by attachment probabilities
            citation_probs.sort_values('citation_prob', ascending=False,
                                       kind='mergesort', inplace=True)

            # case rankings (CL ids)
            # return np.array([e[1] for e in citation_probs.index])
            ancestor_ranking = np.array([e.split('_')[1] for e in citation_probs.index])

            rank_scores.loc[test_case['name'], metric] = score_ranking(cited_cases,
                                                                  ancestor_ranking)

            logloss_scores.loc[test_case['name'], metric] = score_logloss(citation_probs,
                                                                          cited_cases)
    return rank_scores, logloss_scores, LogRegs


def fit_LogRegs(subnet_dir, metrics):
    # load edge data for all edges
    tr_edge_data = pd.read_csv(subnet_dir + 'edge_data.csv',
                               index_col=0)

    # store logistic regressions
    LogRegs = {}

    # fit each logistic regression
    for metric in metrics:
        # get columns for log regression
        columns_to_use = get_columns(metrics, metric)

        # fit logistic regression
        LogReg = fit_logistic_regression(tr_edge_data, columns_to_use)
        LogRegs[metric] = LogReg

    return LogRegs


def get_columns(metrics, metric):
    if metric == 'all':
        columns_to_use = copy.deepcopy(metrics)
        columns_to_use.remove('all')
    else:
        columns_to_use = [metric]

    if metric not in ['similarity', 'all']:
        columns_to_use.append('similarity')

    return columns_to_use


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


def logloss(act, pred):
    epsilon = 1e-15
    pred = sp.maximum(epsilon, pred)
    pred = sp.minimum(1-epsilon, pred)
    ll = sum(act*sp.log(pred) + sp.subtract(1,act)*sp.log(sp.subtract(1,pred)))
    ll = ll * -1.0/len(act)
    return ll


def score_logloss(citation_probs, cited_cases):

    # re-index to cases
    citation_probs.index = [e.split('_')[1] for e in citation_probs.index]
    citation_probs['is_edge'] = 0
    citation_probs.loc[cited_cases, 'is_edge'] = 1

    # get list of predicted probs and citaiton indicators
    y_act = citation_probs['is_edge'].tolist()
    prob = citation_probs['citation_prob'].tolist()

    return logloss(y_act, prob)
