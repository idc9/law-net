import numpy as np
import cPickle as pickle
from pipeline_helper_functions import *
from sklearn.metrics.pairwise import cosine_similarity


def save_similarity_matrix(experiment_data_dir, similarity_matrix,
                           CLid_to_index):
    """
    saves similarity matrix and CLid_to_index dict
    """

    # save similarity matrix
    save_sparse_csr(filename=experiment_data_dir + 'cosine_sims',
                    array=S)

    # save clid to index map
    with open(experiment_data_dir + 'CLid_to_index.p', 'wb') as fp:
        pickle.dump(CLid_to_index, fp)


def load_similarity_matrix(experiment_data_dir):
    """
    Load similarity matrix and CLid_to_index dict

    Parameters
    ----------
    experiment_data_dir:

    Output
    ------
    similarity_matrix, CLid_to_index

    >>> similarity_matrix, CLid_to_index = load_similarity_matrix(experiment_data_dir)
    """
    similarity_matrix = load_sparse_csr(filename=experiment_data_dir + 'cosine_sims.npz')

    with open(experiment_data_dir + 'CLid_to_index.p', 'rb') as f:
        CLid_to_index = pickle.load(f)

    return similarity_matrix, CLid_to_index


def get_similarity(similarity_matrix, CLid_pair, CLid_to_index):
    """
    Workhorse function for get_similarities
    """
    try:
        ida = CLid_to_index[CLid_pair[0]]
        idb = CLid_to_index[CLid_pair[1]]

        return similarity_matrix[ida, idb]
    except KeyError:
        return np.nan


def get_similarities(similarity_matrix, CLid_pair, CLid_to_index):
    """
    Returns the similarities for cases index by CL ids as a list from
    precomuted similarity matrix

    Parameters
    ----------
    similarity_matrix: precomputed similarity matrix

    CLid_pair: lists of CL id pairs whose similarities we want

    CLid_to_index: dict that maps CL ids to similarity_matrix indices
    """
    return [get_similarity(similarity_matrix, pair, CLid_to_index) for pair in CLid_pair]


def compute_similarity(tfidf_matrix, CLid_pairs, CLid_to_index):
    """
    Workhorse helper function for compute_similarities
    """
    try:
        ida = CLid_to_index[CLid_pairs[0]]
        idb = CLid_to_index[CLid_pairs[1]]

        return cosine_similarity(tfidf_matrix[ida, :],
                                 tfidf_matrix[idb, :])
    except KeyError:
        return np.nan


def compute_similarities(tfidf_matrix, CLid_pair, CLid_to_index):
    """
    Returns the similarities for cases index by CL ids as a list by computing
    them from tfidf matrix.

    Parameters
    ----------
    similarity_matrix: precomputed similarity matrix

    CLid_pair: lists of CL id pairs whose similarities we want

    CLid_to_index: dict that maps CL ids to similarity_matrix indices
    """
    return [compute_similarity(tfidf_matrix, pair, CLid_to_index) for pair in CLid_pair]
