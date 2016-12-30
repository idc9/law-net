from __future__ import division
import pandas as pd
import numpy as np
import re
import copy
from math import *
from datetime import datetime

from pipeline_helper_functions import *
from custom_vertex_metrics import *


def make_snapshot_vertex_metrics(G, active_years, vertex_metrics,
                                 subnet_dir, print_progress=True,
                                 overwrite=False):
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

    # directory where we save the snapshot dataframes
    sn_dir = subnet_dir + 'snapshots/'

    # maybe kill old snapshot files if there are already some in the directory
    if overwrite:
        files_in_dir = os.listdir(sn_dir)

        for f in files_in_dir:
            os.remove(sn_dir + f)

    # include year before min active year
    all_years = copy.copy(active_years)
    all_years.append(min(active_years) - 1)

    # create a vertex df for each year T
    i = 0
    for year in all_years:
        i += 1
        if print_progress:
            if int(log(i+1, 2)) == log(i+1, 2):
                current_time = datetime.now().strftime('%H:%M:%S')
                print 'year %d, (%d/%d) at %s' % (year, i + 1,
                                                  len(all_years), current_time)

        # get subgraph at particular time
        G_T = get_network_at_time(G, year)

        # creates dataframe using 'name' attribute as index because
        # it is consistent throughout all truncations of the network
        df_T = pd.DataFrame(index=G_T.vs['name'])
        df_T.index.name = 'CLid'
        df_T['year'] = G_T.vs['year']

        # add column for each metric
        for metric in vertex_metrics:
            df_T[metric] = create_metric_column(G_T, metric, year)

        file_path = sn_dir + 'vertex_metrics_' \
                                        + str(year) + '.csv'
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


def create_metric_column(G, metric, year=None):
    """
    Returns an array of the pageranks for vertices in a network G

    Parameters
    ------------
    G: igraph network object where each node has a time attribute

    metric: string of the vertex metrics we want to compute
    (pagerank, indegree, etc)

    year: is year of the network if we are passing a time truncated network

    - indegree
    - outdegree
    - degree
    - d_pagerank
    - u_pagerank
    - d_closeness
    - u_closeness
    - d_betweenness
    - u_betweenness
    - authorities
    - hubs
    - d_eigen
    - u_eigen

    d_ means for directed graph
    u_ means for undirected graph
    Output
    -------
    metric: an array of size G.vs that contains the metric for G's vertices
            or does not return value on invalid metric parameter
    """

    try:
        # calculates metric which matched parameter
        if metric == 'indegree':
            metric_column = G.indegree()
        elif metric == 'outdegree':
            metric_column = G.outdegree()
        elif metric == 'degree':
            metric_column = G.degree()
        elif metric == 'd_pagerank':
            # scale page rank by number of nodes
            scaled_pr_vals = np.array(G.pagerank()) * len(G.vs)
            metric_column = scaled_pr_vals.tolist()
        elif metric == 'u_pagerank':
            # scale page rank by number of nodes
            scaled_pr_vals = np.array(G.as_undirected().pagerank()) * len(G.vs)
            metric_column = scaled_pr_vals.tolist()
        elif metric == 'd_closeness':
            metric_column = G.closeness(mode="IN", normalized=True)
        elif metric == 'u_closeness':
            metric_column = G.as_undirected().closeness(normalized=True)
        elif metric == 'd_betweenness':
            metric_column = G.betweenness(directed=True)
        elif metric == 'u_betweenness':
            metric_column = G.as_undirected().betweenness(directed=True)
        elif metric == 'authorities':
            metric_column = G.authority_score()
        elif metric == 'hubs':
            metric_column = G.hub_score(scale=True)
        elif metric == 'd_eigen':
            metric_column = G.eigenvector_centrality()
        elif metric == 'u_eigen':
            metric_column = G.as_undirected().eigenvector_centrality()
        elif 'recentcite' in metric:
            # metric == recentcite_10 means threshold = 10
            current_year = year
            threshold = int(metric.split('_')[-1])

            metric_column = get_recent_citations(G, current_year, threshold)

    except Exception:
        print 'problem with %s' % metric
        metric_column = metric_column = [np.nan] * len(G.vs)

    return metric_column
