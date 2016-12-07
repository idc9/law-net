import glob
import numpy as np
import random as random
import pandas as pd


def compute_ranking_metrics(G, LogReg, columns_to_use,
                            experiment_data_dir, year_interval, R):
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

    Output
    -------
    The average ranking score over all R cases we tested
    '''

    # select cases for sample
    vertices = set(G.vs)
    cases_to_test = random.sample(vertices, R)

    cases_to_test_rank_scores = []

    # load all the vertex metric dataframes into a dict so
    # they only have to be read in once
    path_to_vertex_metrics_folder = experiment_data_dir + 'snapshots/'
    all_vertex_metrics_df = glob.glob(path_to_vertex_metrics_folder + "/vertex_metrics*.csv")

    vertex_metric_dict = {}
    for vertex_metrc_df in all_vertex_metrics_df:
        # add df to dict with filepath as key
        vertex_metric_dict[vertex_metrc_df] = pd.read_csv(vertex_metrc_df,
                                                          index_col=0)

    # calculate each case's score
    for case in cases_to_test:

        # determine which vertex_df to retrieve
        year = case['year'] + (year_interval - case['year'] % year_interval)

        # look-up that dataframe from given path
        vertex_df = vertex_metric_dict[path_to_vertex_metrics_folder + 'vertex_metrics_' + str(year) + '.csv']

        # create df that the logistical regression object will evaluate
        x_test_df = vertex_df[columns_to_use]
        attachment_p = get_attachment_probabilty(LogReg,
                                                 x_test_df)

        # add the attachment probabilities as column
        vertex_df['attachment_p'] = attachment_p
        # sort by attachment probabilities
        vertex_df = vertex_df.sort_values('attachment_p',
                                          ascending=False,
                                          kind='mergesort')

        # get neighbors
        neighbors = G.neighbors(case.index, mode='OUT')

        # rank and score neighbors using dataframe indices
        scores = []  # list of scores for each vertex
        for i in neighbors:
            rank = vertex_df.index.get_loc(G.vs[i]['name']) + 1
            score = 1-rank/len(attachment_p)
            scores.append(score)

        case_rank_score = sum(scores)  # sum up the scores for each case

        # add score to list of all cases' scores
        cases_to_test_rank_scores.append(case_rank_score)

    return np.mean(cases_to_test_rank_scores)


def get_attachment_probabilty(LogReg, x_test_df):
    '''
    Evaluates our logistic regression model for a given dataset.

    Parameters
    ------------
    LogReg: a logistic regression object
    (i.e. the output of fit_logistic_regression)

    x_test_df: columns of vertex_df used in evaluating the
    logistical regression

    Output
    ------
    returns a list of attachment probabilities for the dataset
    '''

    # get attachment probabilities on testing set
    prob = LogReg.predict_proba(x_test_df)

    # predicted probabilities for ALL case for edge present (1)
    prob_present = prob[:, 1:2]
    # convert to list
    prob_present_list = [i.tolist()[0] for i in prob_present]

    return prob_present_list
