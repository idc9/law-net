import glob
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix


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


def save_sparse_csr(filename, array):
    """
    saves a sparse CSR matrix
    from http://stackoverflow.com/questions/8955448/save-load-scipy-sparse-csr-matrix-in-portable-data-format
    """
    np.savez(filename, data=array.data, indices=array.indices,
             indptr=array.indptr, shape=array.shape)


def load_sparse_csr(filename):
    """
    Loads a saved CSR matrix
    """
    loader = np.load(filename)
    return csr_matrix((loader['data'], loader['indices'], loader['indptr']),
                      shape=loader['shape'])
