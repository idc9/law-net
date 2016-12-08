import glob
import numpy as np
import random as random
import pandas as pd

from pipeline_helper_functions import *


def compute_ranking_metrics(G,
                            LogReg,
                            columns_to_use,
                            experiment_data_dir,
                            snapshot_year_list,
                            R,
                            seed=None):
    '''
    Computes the rank score metric for a given logistic regression object.

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

    seed: random seed for selecting cases whose ancsetry to score

    Output
    -------
    The average ranking score over all R cases we tested
    '''

    if seed:
        random.seed(seed)

    # select cases for sample
    vertices = set(G.vs)
    cases_to_test = random.sample(vertices, R)

    test_case_rank_scores = []
    test_case_out_degrees = []

    # load snapshots
    snapshots_dict = load_snapshots(experiment_data_dir, train=True)

    # similarity_matrix = pd.read_csv(experiment_data_dir + 'similarity_matrix.csv', index_col=0)
    similarity_matrix = 0

    # calculate each case's score
    for ing_case in cases_to_test:
        ing_year = ing_case['year']

        # get neighbors
        actual_citations = G.neighbors(ing_case.index, mode='OUT')
        num_citations = len(actual_citations)

        # only score cases who cite at least one case
        if num_citations >= 1:

            # determine which vertex_df to retrieve
            snapshot_year = get_snapshot_year(ing_case['year'],
                                              snapshot_year_list)

            # look-up that dataframe from given path
            snapshot_df = snapshots_dict['vertex_metrics_' +
                                         str(snapshot_year)]

            # restrict ourselves to ancestors of ing case
            ancentors = [v.index for v in G.vs.select(year_le=ing_year)]
            num_ancentors = len(ancentors)

            # all edges from ing case to previous cases
            edgelist = zip([ing_case.index] * len(ancentors), ancentors)

            # compute edge data
            edge_data = get_edge_data(G, edgelist, snapshot_df,
                                      similarity_matrix, edge_status=None)

            # probability a case is cited
            citation_probs = get_attachment_probabilty_logreg(LogReg,
                                                              edge_data)

            # sort by attachment probabilities
            citation_probs.sort_values('citation_prob', ascending=False,
                                       kind='mergesort', inplace=True)

            # case rankings (CL ids)
            cases_ranking = np.array([int(e.split('_')[1])
                                      for e in citation_probs.index])

            # keep track of how many citations case has
            # test_case_out_degrees.append(num_citations)

            # rank and citaions
            case_scores = []
            # case_ranks = [] # could keep track of this if we wanted

            for cited_ig in actual_citations:

                # CL id of actual citation
                cited = int(G.vs[cited_ig]['name'])

                # where cited case was ranked
                rank = np.where(cases_ranking == cited)[0][0]

                # score the ranking
                rank_score = get_rank_score(rank, num_ancentors)

                case_scores.append(rank_score)
                # case_ranks.append(rank)

            # average over all citations
            avg_rank_score = np.mean(case_scores)

            # add score to list of all cases' scores
            test_case_rank_scores.append(avg_rank_score)

    return test_case_rank_scores


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


def get_rank_score(position, number_of_items):
    """
    Computes the rank score (1 is good)

    See Zanin et al. (pref attachemnt aging ...)

    Parameters
    ----------
    position: where the item is ranked

    number_of_items: how many items were ranked
    """
    return 1.0 - float(position) / (number_of_items - 1.0)
