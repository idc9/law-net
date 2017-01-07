import glob
import numpy as np
import random as random
import pandas as pd
from math import *
from datetime import datetime
import copy
from scipy.stats import rankdata


from sklearn.metrics import log_loss
import scipy as sp

from experiment_helper_functions import *
from pipeline_helper_functions import *
from attachment_model_inference import *
from bag_of_words import *
from rank_loss_functions import *


def get_rankscores_LR(G, test_cases, metrics, subnet_dir,
                      metric_normalization=None):
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

    # predictiion loss: error rate, logloss
    ERR = pd.DataFrame(index=[c['name'] for c in test_cases], columns=metrics)
    LL = pd.DataFrame(index=[c['name'] for c in test_cases], columns=metrics)

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
            ranking = get_attachment_probabilty_logreg(LogReg,
												       edge_data[columns_to_use])

            scores = ranking['citation_prob']
            ranking['rank'] = np.floor(rankdata(scores, method='average'))
            ranking.index = [e[1] for e in ranking.index]

            # ranking loss
            mrs = get_mean_rankscore(cited_cases, ranking)
            rr = get_reciprocal_rank(cited_cases, ranking)
            pak100 = get_precision_at_K(cited_cases, ranking, 100)
            pak1000 = get_precision_at_K(cited_cases, ranking, 1000)

            # preidction loss
            predictions = get_predictions(cited_cases, ranking)
            err = get_error_rate(predictions)
            ll = get_logloss(predictions)

            # update data frames
            MRS.loc[test_case['name'], metric] = mrs
            RR.loc[test_case['name'], metric] = rr
            PAK100.loc[test_case['name'], metric] = pak100
            PAK1000.loc[test_case['name'], metric] = pak1000
            ERR.loc[test_case['name'], metric] = err
            LL.loc[test_case['name'], metric] = ll

        ranking_loss = {'MRS': MRS,
                        'RR': RR,
                        'PAK100': PAK100,
                        'PAK1000': PAK1000,
                        'ERR': ERR,
                        'LL': LL}

    return ranking_loss, LogRegs


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

    X: columns of vertex_df  used in evaluating the
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


def get_predictions(cited_cases, ranking):
    """
    Given the citation_probs df and list of cited cases returns the
    predictions df with columns 'pred_prob' and 'y'
    """
    # re-index to cases
    predictions = pd.DataFrame(columns=['pred_prob', 'y'],
                               index=ranking.index)

    # add classification labels
    predictions['y'] = 0
    predictions.loc[cited_cases, 'y'] = 1

    # add prediction probabilities
    predictions['pred_prob'] = ranking['citation_prob'].tolist()

    return predictions.reset_index(drop=True, inplace=False)
