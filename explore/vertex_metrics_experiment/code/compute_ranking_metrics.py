import glob
import numpy as np
import random as random
import pandas as pd
from math import *
from datetime import datetime

from pipeline_helper_functions import *
from similarity_matrix import *
from get_edge_data import *


def get_test_case_scores_LR(G, test_cases, snapshots_dict,
                            similarity_matrix, CLid_to_index,
                            LogReg, columns_to_use, print_progress=False):
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

        score = get_score_LR(G, test_case, snapshots_dict, similarity_matrix,
                             CLid_to_index, LogReg, columns_to_use)

        scores[test_case['name']] = score

    return scores


def get_score_LR(G, test_case, snapshots_dict, similarity_matrix,
                 CLid_to_index, LogReg, columns_to_use):
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
                              similarity_matrix, CLid_to_index,
                              edge_status=None)

    # case rankings (CL ids)
    ancestor_ranking = get_case_ranking_logreg(edge_data,
                                               LogReg,
                                               columns_to_use)

    # compute rank score
    score = score_ranking(cited_cases, ancestor_ranking)

    return score


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
