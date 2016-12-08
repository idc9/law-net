import glob
import pandas as pd
import numpy as np

def load_snapshots(experiment_data_dir, train=True):
    """
    Loads the snapshot data frames into a dict indexed by the file names

    Parameters
    ----------
    experiment_data_dir: path to experiment data files

    Output
    ------
    python dict
    """
    # load all the vertex metric dataframes into a dict so
    # they only have to be read in once
    if train:
        snap_stub = 'snapshots_train/'
    else:
        snap_stub = 'snapshots/'

    path_to_vertex_metrics_folder = experiment_data_dir + snap_stub

    snapshot_paths = glob.glob(path_to_vertex_metrics_folder + \
                               "/vertex_metrics*.csv")
    snapshots_dict = {}
    for path in snapshot_paths:

        # snapshot file name is key
        snapshot_key = path.split(snap_stub)[1].split('.csv')[0]
        snapshots_dict[snapshot_key] = pd.read_csv(path, index_col=0)

    return snapshots_dict


def get_snapshot_year(ing_year, snapshot_year_list):
    """
    Returns the smallest year greater than ing year
    """
    return min([y for y in snapshot_year_list if ing_year < y])


def get_edge_data(G, edgelist, snapshot_df, similarity_matrix, edge_status=None):
    """
    Returns a data frame for all edges from given edge list
    """

    num_edges = len(edgelist)

    # CL ids of ed cases (indexes the snap_df rows)
    ed_CLids = [G.vs[edge[1]]['name'] for edge in edgelist]
    ing_CLids = [G.vs[edge[0]]['name'] for edge in edgelist]

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

    # create edge data frame
    edge_data = pd.DataFrame()
    edge_data['indegree'] = ed_metrics['indegree'].tolist()
    edge_data['l_pagerank'] = ed_metrics['l_pagerank'].tolist()

    edge_data['age'] = ing_year - ed_year
    edge_data['similarity'] = similarities

    # add edge status
    if edge_status == 'present':
        is_edge = [1] * num_edges
    elif edge_status == 'absent':
        is_edge = [0] * num_edges
    else:
        # TODO: check if edge is present
        is_edge = [-999] * num_edges

    edge_data['is_edge'] = is_edge

    edge_data.index = [str(edge[0]) + '_' + str(edge[1]) for edge in edgelist]
    edge_data.index.name = 'CLids'

    return edge_data


def edge_data_row(citing_vertex, cited_vertex, ing_snapshot_df):
    """
    Returns one row of the edge data frame

    Parameters
    ----------
    citing_vertex, cited_vertex: igraph vertices

    ing_snapshot_df: vertex metrics from ing's year (data frame)

    Output
    ------
    returns a tuple
    """
    # TODO: can probably kill this

    # grab vertex metadata
    citing_name = citing_vertex['name'][0]
    cited_name = cited_vertex['name'][0]
    citing_year = citing_vertex['year'][0]
    cited_year = cited_vertex['year'][0]

    cited_vertex_metrics = ing_snapshot_df.loc[cited_name].values.tolist()

    return (class_label) + \
           (citing_name, cited_name, citing_year, cited_year) + \
           (citing_year - cited_year) + \
           tuple(cited_vertex_metrics)
