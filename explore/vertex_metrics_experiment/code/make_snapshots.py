
from __future__ import division
import pandas as pd
from pipeline_helper_functions import *
import numpy as np
import re


def make_snapshot_vertex_metrics(G, active_years, vertex_metrics,
                                 experiment_data_dir):
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
    # include year before min active year
    active_years.append(min(active_years) - 1)

    # create a vertex df for each year T
    for T in active_years:
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


def create_metric_column(G, metric):
    """
    Returns an array of the pageranks for vertices in a network G

    Parameters
    ------------
    G: igraph network object where each node has a time attribute

    metric: string of the vertex metrics we want to compute
    (pagerank, indegree, etc)

    Output
    -------
    metric: an array of size G.vs that contains the metric for G's vertices
            or does not return value on invalid metric parameter
    """
    # calculates metric which matched parameter
    if metric == 'pagerank':
        metric_column = G.pagerank()
    elif metric == 's_pagerank':
        # scale page rank by number of nodes
        pr_vals = G.pagerank()
        num_nodes = len(G.vs)
        metric_column = [pr * num_nodes for pr in pr_vals]
    elif metric == 'indegree':
        metric_column = G.indegree()
    elif metric == 'hubs':
        metric_column = G.hub_score(scale=True)
    else:
        raise ValueError('%s not implemented' % metric)

    return metric_column
