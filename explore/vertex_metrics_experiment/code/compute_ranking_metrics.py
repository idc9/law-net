import glob
import numpy as np
import random as random
import pandas as pd
from math import *
from datetime import datetime

from pipeline_helper_functions import *
from similarity_matrix import *
from get_edge_data import *


def compute_ranking_metrics_LR(G,
                               LogReg,
                               columns_to_use,
                               experiment_data_dir,
                               active_years,
                               R,
                               year_floor=1900,
                               seed=None,
                               print_progress=False):
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
    # ranking scores for each test case
    test_case_rank_scores = []

    # get list of test cases
    test_vertices = get_test_cases(G, active_years, R, seed=seed)

    # load snapshots
    snapshots_dict = load_snapshots(experiment_data_dir)

    # mabye load the similarities
    if 'similarity' in columns_to_use:
        similarity_matrix, CLid_to_index = load_similarity_matrix(experiment_data_dir)
    else:
        similarity_matrix = None
        CLid_to_index = None

    # run until we get R test cases (some cases might not have any citations)
    for i in range(R):
        if print_progress:
            if int(log(i+1, 2)) == log(i+1, 2):
                current_time = datetime.now().strftime('%H:%M:%S')
                print '(%d/%d) at %s' % (i + 1, R, current_time)

        # randomly select a case
        test_case = test_vertices[i]

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
                                  similarity_matrix, CLid_to_index,
                                  edge_status=None)

        # case rankings (CL ids)
        ancestor_ranking = get_case_ranking_logreg(edge_data,
                                                   LogReg, columns_to_use)

        # compute rank score
        score = score_ranking(cited_cases, ancestor_ranking)

        test_case_rank_scores.append(score)

    # return test_case_rank_scores, case_ranks, test_cases
    return test_case_rank_scores


def get_test_cases(G, active_years, num_test_cases, seed=None):
    """
    Get a list of test cases
    - test cases must have at least one citation
    - cited case year must be strictly less than citing case year

    Parameters
    ----------
    G: igraph object

    active_years: list of possible citing years

    num_test_cases: number of test cases

    seed: seed for sampling vertices

    Output
    ------
    returns a list of test cases (igraph vertices)
    """

    # seed for selecting test cases
    if seed:
        random.seed(seed)

    # select cases for sample
    possible_citing_cases = set(G.vs.select(year_ge=min(active_years),
                                            year_le=max(active_years)))

    # other data we might want to keep track of
    test_cases = set()

    # run until we get enough test cases
    while(len(test_cases) < num_test_cases):

        # randomly select a case
        test_case = random.sample(possible_citing_cases, 1)[0]

        # test case citing year
        ing_year = test_case['year']

        # get neighbors first as ig index
        cited_cases = G.neighbors(test_case.index, mode='OUT')

        # only keep cited cases coming in years strictly before citing year
        cited_cases_pre = [ig_id for ig_id in cited_cases
                           if G.vs[ig_id]['year'] < ing_year]

        # only add cases who have at least one citation
        if len(cited_cases_pre) >= 1:
            # make sure case has already been added
            if test_case not in test_cases:
                test_cases.add(test_case)

    return list(test_cases)


def get_cited_cases(G, citing_vertex):
    """
    Returns the ciations of a cases whose cited year
    is strictly less than citing year

    Parameters
    ----------
    G: igraph object

    citing_vertex: igraph vertex

    Output
    ------
    list of CL ids of cited cases
    """

    # get neighbors first as ig index
    all_citations = G.neighbors(citing_vertex.index, mode='OUT')

    # return CL indices of cases
    # only return cited cases whose year is stictly less than citing year
    return [G.vs[ig_id]['name'] for ig_id in all_citations
            if G.vs[ig_id]['year'] < citing_vertex['year']]


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
    return np.array([e.split('_')[1] for e in citation_probs.index])


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


def score_ranking(cited_cases, ancestor_ranking):
    """
    Retuns the rank score for a case

    Parameters
    ----------
    cited_cases: list of cases that were cited

    cases_ranking: ranking of all ancestors

    Output
    ------
    average of cited case rank scores
    """

    case_scores = []

    # number of ancestors
    num_items = len(ancestor_ranking)

    # compute rank score for each case test case actually cited
    for case in cited_cases:

        # where cited case was ranked
        rank = np.where(ancestor_ranking == case)[0][0]

        # score the ranking
        rank_score = get_rank_score(rank, num_items)

        case_scores.append(rank_score)

    return np.mean(case_scores)
