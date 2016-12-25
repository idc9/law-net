import numpy as np
import pandas as pd

from pipeline_helper_functions import *
from similarity_matrix import *


def get_edge_data(G, edgelist, snapshot_df, columns_to_use,
                  similarity_matrix, CLid_to_index,
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

    similarity_matrix: precomputed similarities
    CLid_to_index: dict that maps CL ids to indices of similarity_matrix

    edge_status: are the edges all present or absent or do we need to find out
    """

    num_edges = len(edgelist)

    # CL ids of ed cases (indexes the snap_df rows)
    ed_CLids = [G.vs[edge[1]]['name'] for edge in edgelist]
    ing_CLids = [G.vs[edge[0]]['name'] for edge in edgelist]

    # ages
    ed_year = np.array([G.vs[edge[1]]['year'] for edge in edgelist])
    ing_year = np.array([G.vs[edge[0]]['year'] for edge in edgelist])

    # ed metrics in ing year
    # note snapshot_df indices are ints
    ed_metrics = snapshot_df.loc[[int(i) for i in ed_CLids]]

    # initialize edge data frame
    edge_data = pd.DataFrame()

    # add columns to edge data frame
    for metric in columns_to_use:
        if metric in ed_metrics.columns:
            edge_data[metric] = ed_metrics[metric].tolist()
        elif metric == 'age':
            edge_data[metric] = ing_year - ed_year
        elif metric == 'decayed_indegree':
            halflife = 10
            edge_data[metric] = 2.0 ** ((ing_year - ed_year)/halflife) * edge_data['indegree']
        elif metric == 'similarity':
            edge_data[metric] = get_similarities(similarity_matrix,
                                                 zip(ing_CLids, ed_CLids),
                                                 CLid_to_index)

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

    edge_data.index = [str(ing_CLids[i]) + '_' + str(ed_CLids[i])
                       for i in range(num_edges)]
    edge_data.index.name = 'CLids'

    return edge_data
