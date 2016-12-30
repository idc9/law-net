import numpy as np
import pandas as pd

from pipeline_helper_functions import *
from bag_of_words import *

# list of possible vertex metrics
vertex_metrics = ['indegree', 'outdegree', 'degree', 'd_pagerank',
                  'u_pagerank', 'd_closeness', 'u_closeness',
                  'd_betweenness', 'u_betweenness', 'authorities',
                  'hubs', 'd_eigen', 'u_eigen']


def get_edge_data(G, edgelist, snapshot_df, columns_to_use,
                  tfidf_matrix=None, op_id_to_bow_id=None,
                  metric_normalization=None, edge_status=None):
    """
    Returns a data frame for all edges from given edge list
    for a given snapshot

    Parameters
    ----------
    G: graph (igraph object)

    edgelist: igraph indices of edges whose data to get

    snapshot_df: dictionary containing the snapshot information

    columns_to_use: list of columns to use

    tfidf_matrix: precomputed tfidf_matrix
    op_id_to_bow_id: dict that maps CL ids to indices of tdidf matrix

    edge_status: are the edges all present or absent or do we need to find out

    metric_normalization: normalize the snapshot metrics
    """

    # make sure columns_to_use is a list
    if type(columns_to_use) == str:
        columns_to_use = [columns_to_use]

    num_edges = len(edgelist)

    # CL ids of ed cases (indexes the snap_df rows)
    ed_op_ids = [G.vs[edge[1]]['name'] for edge in edgelist]
    ing_op_ids = [G.vs[edge[0]]['name'] for edge in edgelist]

    # ages
    ed_year = np.array([G.vs[edge[1]]['year'] for edge in edgelist])
    ing_year = np.array([G.vs[edge[0]]['year'] for edge in edgelist])

    # ed metrics in ing year
    # note snapshot_df indices are ints
    ed_metrics = snapshot_df.loc[[int(i) for i in ed_op_ids]]

    # initialize edge data frame
    edge_data = pd.DataFrame()

    # add columns to edge data frame
    for metric in columns_to_use:

        # which vertex metrics from the snapshot df to grab
        # i.e. only grab vertex metric columns
        vertex_metrics_to_use = set(ed_metrics.columns).intersection(vertex_metrics)

        if metric in vertex_metrics_to_use:
            edge_data[metric] = ed_metrics[metric].tolist()
        elif metric == 'age':
            edge_data[metric] = ing_year - ed_year
        elif metric == 'ing_year':
            edge_data[metric] = ing_year
        elif metric == 'ed_year':
            edge_data[metric] = ed_year
        elif metric == 'similarity':
            edge_data[metric] = compute_similarities(ing_op_ids, ed_op_ids,
                                                     tfidf_matrix,
                                                     op_id_to_bow_id)

    # possibly normalize metrics
    if metric_normalization:

        # only normalize graph vertex metrics i.e. not age
        metrics_to_normalize = set(columns_to_use).intersection(set(vertex_metrics))

        # normalize metics that deserve it
        for metric in metrics_to_normalize:
            values = edge_data[metric]
            scaling = get_scaling(values, metric_normalization, alpha=.05)
            edge_data[metric] = values / scaling

    # add edge status
    if edge_status is not None:
        if edge_status == 'present':
            is_edge = [1] * num_edges
        elif edge_status == 'absent':
            is_edge = [0] * num_edges
        elif edge_status == 'find':
            # look up edge status
            is_edge = [int(edge_is_present(G, e[0], e[1])) for e in edgelist]

        edge_data['is_edge'] = is_edge

    edge_data.index = [str(ing_op_ids[i]) + '_' + str(ed_op_ids[i])
                       for i in range(num_edges)]
    edge_data.index.name = 'CLids'

    return edge_data


def get_scaling(values, scaling, alpha=.05):
    """
    Returns scaling
    """
    if scaling == 'mean':
        return np.mean(values)

    # robust mean
    elif scaling == 'upper trimmed mean':
        upper_bound = np.percentile(values, 1 - alpha)
        values_trimmed = values[values <= upper_bound]
        return np.mean(values_trimmed)
    elif scaling == 'lower trimmed mean':
        lower_bound = np.percentile(values, alpha)
        values_trimmed = values[values >= lower_bound]
        return np.mean(values_trimmed)
    elif scaling == 'trimmed mean':
        upper_bound = np.percentile(values, 1 - alpha)
        lower_bound = np.percentile(values, alpha)

        values_trimmed = values[(values >= lower_bound) & (values <= upper_bound)]
        return np.mean(values_trimmed)

    elif scaling == 'median':
        return np.median(values)
    elif scaling == 'max':
        return np.max(values)

    elif scaling == 'percentile':
        return np.percentile(values, alpha)

    else:
        raise ValueError('%s not implemented' % scaling)
