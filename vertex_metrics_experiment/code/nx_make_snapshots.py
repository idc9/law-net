import pandas as pd
import numpy as np
import re
import copy
from math import *
from datetime import datetime
import networkx as nx

from pipeline_helper_functions import *
from custom_vertex_metrics import *


def update_snapshot_vertex_metrics_nx(G, active_years, to_add, subnet_dir):
    """
    Creates the data frames with vertex metics in given years
    This function is for a networkx graph

    Parameters
    -----------
    G: networkx network object with each node assigned a year

    years: sequence of years we want to compute

    vertex_metrics: which vertex metrics we want to compute
    (pagerank, indegree, etc)

    data_dir: path to generated data folder

    Output
    --------
    writes csv files of the vertex metric data frame for each year in years
    """

    # directory where we save the snapshot dataframes
    sn_dir = subnet_dir + 'snapshots/'

    # include year before min active year
    all_years = copy.copy(active_years)
    all_years.append(min(active_years) - 1)

    # create a vertex df for each year T
    for year in all_years:

        # read in pre-made snapshot
        file_path = sn_dir + 'vertex_metrics_' + str(year) + '.csv'
        df_T = pd.read_csv(file_path, index_col=0)

        # get subgraph at particular time
        G_T = get_network_at_time_nx(G, year)

        # add column for each metric
        for metric in to_add:
            df_T[metric] = create_metric_column(G_T, metric, year)

        # save update
        df_T.to_csv(file_path, index=True)


def get_network_at_time_nx(G, T):
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
    G_T: a networkx object of what the network looked like at time T
    """
    # TODO: make this work for networkx
    # # select vertices whose year is less than or equal to T
    # vertices = G.vs.select(year_le=T)
    # # create a subgraph based on those vertices
    # G_T = G.subgraph(vertices)
    # return G_T
    pass


def create_metric_column(G, metric, year=None):
    """
    Returns an array of the pageranks for vertices in a network G

    Parameters
    ------------
    G: igraph network object where each node has a time attribute

    metric: string of the vertex metrics we want to compute
    (pagerank, indegree, etc)

    year: is year of the network if we are passing a time truncated network

    - katz


    d_ means for directed graph
    u_ means for undirected graph
    Output
    -------
    metric: an array of size G.vs that contains the metric for G's vertices
            or does not return value on invalid metric parameter
    """

    try:
        # calculates metric which matched parameter
        if metric == 'katz':
            metric_column = nx.katz_centrality(Gnx)

    except Exception:
        print 'problem with %s' % metric
        metric_column = metric_column = [np.nan] * len(G.vs)

    return metric_column
