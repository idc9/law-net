
from __future__ import division
import pandas as pd
from pipeline_helper_functions import *
import numpy as np
import re


def get_snapshot_vertex_metrics(G, years, vertex_metrics, experiment_data_dir):
    """
    Creates the data frames with vertex metics in given years

    Parameters
    -----------
    G: igraph network object with each node assigned a year

    years: sequence of years we want to compute

    vertex_metrics: which vertex metrics we want to compute
    (pagerank, indegree, etc)

    data_dir: path to generated data folder

    Output
    --------
    writes csv files of the vertex metric data frame for each year in years
    """

    # create a vertex df for each year T
    for T in years:
        # get subgraph at particular time
        G_T = get_network_at_time(G, T)

        # creates dataframe using 'name' attribute as index because
        # it is consistent throughout all truncations of the network
        df_T = pd.DataFrame(index=G_T.vs['name'])
        df_T.index.name = 'CLid'
        df_T['year'] = G_T.vs['year']

        # add column for each metric
        for metric in vertex_metrics:
            df_T[metric] = create_metric_column(G_T, metric)

        file_path = experiment_data_dir + 'snapshots/vertex_metrics_' \
                                        + str(T) + '.csv'
        df_T.to_csv(file_path, index=True)


def get_network_at_time(G, T):
    """
    Returns the subgraph of what the network G looked like at time T
    (i.e. all cases upto and including time T and their
    citations to previous cases)

    Parameters
    ------------
    G: igraph network object where each node has a time attribute

    T: year to truncate at

    Output
    -------
    G_T: an igraph object of what the network looked like at time T
    """
    # select vertices whose year is less than or equal to T
    vertices = G.vs.select(year_le=T)
    # create a subgraph based on those vertices
    G_T = G.subgraph(vertices)
    return G_T


def create_metric_column(G_T, metric):
    """
    Returns an array of the pageranks for vertices in a network G_T

    Parameters
    ------------
    G_T: igraph network object where each node has a time attribute

    metric: string of the vertex metrics we want to compute
    (pagerank, indegree, etc)

    Output
    -------
    metric: an array of size G_T.vs that contains the metric for G_T's vertices
            or does not return value on invalid metric parameter
    """
    # calculates metric which matched parameter
    if metric == 'pagerank':
        metric_column = G_T.pagerank()
    elif metric == 'indegree':
        metric_column = G_T.indegree()
    else:
        return

    return metric_column


def run_transform_snaphots(experiment_data_dir):
    """
    Transforms the raw snapshot data frames into training data
    """
    snapshots_dict = load_snapshots(experiment_data_dir, train=False)

    train_path = experiment_data_dir + 'snapshots_train/'

    for snap in snapshots_dict.keys():
        snapshot_year = int(re.findall(r'\d+', snap)[0])
        snap_train = transform_snaphots(snapshot_df=snapshots_dict[snap],
                                        snapshot_year=snapshot_year)
        snap_train.to_csv(train_path + snap + '.csv',
                          index=True)


def transform_snaphots(snapshot_df, snapshot_year):
    """
    Workhorse function for making transforming raw snapshots
    """
    train_df = pd.DataFrame(index=snapshot_df.index)
    train_df.index.name = 'CLid'

    train_df['indegree'] = snapshot_df['indegree']

    train_df['l_pagerank'] = np.log(snapshot_df['pagerank'])

    train_df['age'] = snapshot_year - snapshot_df['year']

    return train_df
