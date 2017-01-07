import glob
import numpy as np
import random as random
import pandas as pd
from math import *
from datetime import datetime
from scipy.stats import rankdata

from pipeline_helper_functions import *
from get_edge_data import *


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


def get_rank_by_metric(edge_data, metric):
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
    ranking = pd.DataFrame(columns=['rank'],
                           index=[e[1] for e in edge_data.index])

    # larger value of metric is means more likely to be cited
    if metric in ['age']:
        scores = - edge_data[metric]
    else:
        scores = edge_data[metric]

    ranking['rank'] = np.floor(rankdata(scores))

    return ranking
