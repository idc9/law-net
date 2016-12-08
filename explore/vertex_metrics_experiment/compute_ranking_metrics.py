import glob
import numpy as np
import random as random
import pandas as pd


def compute_ranking_metrics(G,
                            LogReg,
                            columns_to_use,
                            experiment_data_dir,
                            year_interval,
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
        np.random.seed(seed)

    # select cases for sample
    vertices = set(G.vs)
    cases_to_test = random.sample(vertices, R)

    test_case_rank_scores = []
    test_case_out_degrees = []

    snapshots_dict = load_snapshots(experiment_data_dir)

    # calculate each case's score
    for ing_case in cases_to_test:
        # get neighbors
        actual_citations = G.neighbors(case.index, mode='OUT')
        num_citations = len(actual_citations)

        # only score cases who cite at least one case
        if num_citations >= 1:

            # determine which vertex_df to retrieve
            year = ing_case['year'] + (year_interval - ing_case['year'] % year_interval)

            # look-up that dataframe from given path
            ing_snapshot_df = snapshots_dict['vertex_metrics_' + str(year)]

            # number of cases in this snapshot
            num_cases = ing_snapshot_df.shape[0]

            # create df that the logistical regression object will evaluate
            x_test_df = make_test_data(G, ing_snapshot_df, ing_vertex, columns_to_use)

            # probability a case is cited
            citation_probs = get_attachment_probabilty_logreg(LogReg, x_test_df)

            # sort by attachment probabilities
            citation_probs.sort_values('citation_prob', ascending=False,
                                       kind='mergesort', inplace=True)


            # keep track of how many citations case has
            test_case_out_degrees.append(num_citations)

            # rank and citaions
            case_scores = []

            for i in actual_citations:
                rank_of_actual_citation = citation_probs.index.get_loc(G.vs[i]['name']) + 1.0
                rank_score = get_rank_score(rank_of_actual_citation, num_cases)
                case_scores.append(rank_score)

            # average over all citations
            avg_rank_score = np.mean(case_scores)

            # add score to list of all cases' scores
            test_case_rank_scores.append(avg_rank_score)

    return test_case_rank_scores


def make_test_data(G, ing_snapshot_df, ing_vertex, columns_to_use):
    # TODO: probably not the right way to to this
    # should copy over the ing_snapshot_df and then add columns
    ed_case_ids = ing_snapshot_df.index

    edgedata_list = []
    for ed_case_id in ed_case_ids:
        cited_vertex = G.vs.find('ed_case_id')
        edgerow = edge_data_row(citing_vertex, cited_vertex, ing_snapshot_df)
        edgedata_list.append()

    column_names = ['edge'] + \
                   ['ing_name', 'ed_name', 'ing_year', 'ed_year', 'age'] + \
                   ['age'] + \
                   snapshots_dict.values()[0].columns.values.tolist()

    df = pd.DataFrame(edgedata_list, columns=column_names)

    return df[columns_to_use]


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
    # TODO: is class 0 citation or class 1??

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
    return 1.0 - float(position) / number_of_items
