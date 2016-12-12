import glob
import numpy as np
import random as random
import pandas as pd

from pipeline_helper_functions import *


def compute_ranking_metrics_LR(G,
                               LogReg,
                               columns_to_use,
                               experiment_data_dir,
                               snapshot_year_list,
                               R,
                               year_floor=1900,
                               seed=None):
    '''
    Computes the rank score metric for a given logistic regression object.

    Sample R test cases that have at least one citation. For each test case
    rank test case's ancestors then compute rank score for test cases actual
    citations.

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

    year_floor: sample only cases after this year

    seed: random seed for selecting cases whose ancsetry to score

    Output
    -------
    The average ranking score over all R cases we tested
    '''

    # seed for selecting test cases
    if seed:
        random.seed(seed)

    # select cases for sample
    vertices = set(G.vs.select(year_ge=1900))

    # ranking scores for each test case
    test_case_rank_scores = []

    # other data we might want to keep track of
    test_cases = []
    test_case_out_degrees = []
    test_case_ranks = []

    # load snapshots
    snapshots_dict = load_snapshots(experiment_data_dir)

    # similarity_matrix = pd.read_csv(experiment_data_dir + 'similarity_matrix.csv', index_col=0)
    similarity_matrix = 0

    # sample until we get R cases (some cases might not have any citations)
    while(len(test_case_rank_scores) < R):

        # randomly select a case
        test_case = random.sample(vertices, 1)[0]

        # test case citing year
        ing_year = test_case['year']

        # get neighbors first as ig index then convert to CLid
        actual_citations = G.neighbors(test_case.index, mode='OUT')
        cited_CLids = [int(G.vs[ig_id]['name']) for ig_id in actual_citations]
        num_citations = len(cited_CLids)

        # only score cases who cite at least one case
        if num_citations >= 1:
            test_cases.append(test_case['name'])

            # determine which vertex_df to retrieve
            snapshot_year = get_snapshot_year(ing_year,
                                              snapshot_year_list)

            # grab data frame of vertex metrics for test case's snapshot
            snapshot_df = snapshots_dict['vertex_metrics_' +
                                         str(snapshot_year)]

            # restrict ourselves to ancestors of ing case
            ancentors = [v.index for v in G.vs.select(year_le=ing_year)]
            num_ancentors = len(ancentors)

            # all edges from ing case to previous cases
            edgelist = zip([test_case.index] * len(ancentors), ancentors)

            # grab edge data
            edge_data = get_edge_data(G, edgelist, snapshot_df, columns_to_use,
                                      similarity_matrix, edge_status=None)

            # case rankings (CL ids)
            cases_ranking = get_case_ranking_logreg(edge_data,
                                                    LogReg, columns_to_use)

            # keep track of how many citations case has
            # test_case_out_degrees.append(num_citations)

            # rank and citaions
            case_scores = []
            case_ranks = []  # could keep track of this if we wanted

            # compute rank score for each case test case actually cited
            for cited in cited_CLids:

                # where cited case was ranked
                rank = np.where(cases_ranking == cited)[0][0]

                # score the ranking
                rank_score = get_rank_score(rank, num_ancentors)

                # maybe keep track of some other data
                case_scores.append(rank_score)
                case_ranks.append(rank)

            # add score to list of all cases' scores
            # test_case_ranks.append(case_ranks)
            test_case_rank_scores.append(np.mean(case_scores))

    # return test_case_rank_scores, case_ranks, test_cases
    return test_case_rank_scores


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
    return np.array([int(e.split('_')[1]) for e in citation_probs.index])


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
