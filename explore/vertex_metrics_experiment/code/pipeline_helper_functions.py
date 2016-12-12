import glob
import pandas as pd
import numpy as np


def load_snapshots(experiment_data_dir):
    """
    Loads the snapshot data frames into a dict indexed by the file names

    Parameters
    ----------
    experiment_data_dir: path to experiment data files

    Output
    ------
    python dict
    """

    path_to_vertex_metrics_folder = experiment_data_dir + 'snapshots/'

    snapshot_paths = glob.glob(path_to_vertex_metrics_folder + \
                               "/vertex_metrics*.csv")
    snapshots_dict = {}
    for path in snapshot_paths:

        # snapshot file name is key
        snapshot_key = path.split('snapshots/')[1].split('.csv')[0]
        snapshots_dict[snapshot_key] = pd.read_csv(path, index_col=0)

    return snapshots_dict


def get_snapshot_year(ing_year, snapshot_year_list):
    """
    Returns the smallest year greater than ing year
    """
    return min([y for y in snapshot_year_list if ing_year <= y])


def get_edge_data(G, edgelist, snapshot_df, columns_to_use, similarity_matrix,
                  edge_status=None):
    """
    Returns a data frame for all edges from given edge list
    """

    num_edges = len(edgelist)

    # CL ids of ed cases (indexes the snap_df rows)
    ed_CLids = [int(G.vs[edge[1]]['name']) for edge in edgelist]
    ing_CLids = [int(G.vs[edge[0]]['name']) for edge in edgelist]

    # ages
    ed_year = np.array([G.vs[edge[1]]['year'] for edge in edgelist])
    ing_year = np.array([G.vs[edge[0]]['year'] for edge in edgelist])

    # get case similarities
    similarities = [0] * num_edges
    for i in range(num_edges):
        # similarities[i] = similarity_matrix.ix[ing_CLids[i], ed_CLids[i]]
        similarities[i] = 0

    # ed metrics in ing year
    ed_metrics = snapshot_df.loc[ed_CLids]

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
            edge_data[metric] = similarities

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


def edge_is_present(G, source, target):
    """
    Returns true of there is an edge from source to target

    Parameters
    source, target: igraph vertex indices

    G: directed igraph object
    """
    return G.get_eid(v1=source, v2=target, directed=True, error=False) != -1


def standardize(X, center=False, scale=False):
    """
    Standardizes a vector

    Parameters
    ---------
    cetner: to center or not to center (by mean)
    scale: to scale or not to scale  (by standard deviation)
    """
    mu = 0
    sigma = 1

    if center:
        mu = np.mean(X)

    if scale:
        sigma = np.std(X)

    return (X - mu)/sigma
