import numpy as np
import cPickle as pickle
from pipeline_helper_functions import *
from sklearn.metrics.pairwise import cosine_similarity

import time


def make_similarity_matrix(subnet_dir, tfidf_matrix,
                           CLid_to_index):
    """
    saves similarity matrix and CLid_to_index dict
    """

    # compute cosine similarities
    start = time.time()

    similarity_matrix = cosine_similarity(tfidf_matrix,
                                          dense_output=True)

    # change data type
    similarity_matrix = similarity_matrix.astype(np.float16)

    # save similarity matrix
    start = time.time()

    np.save(subnet_dir + 'cosine_sims', similarity_matrix)

    # save clid to index map
    with open(subnet_dir + 'CLid_to_index.p', 'wb') as fp:
        pickle.dump(CLid_to_index, fp)


def load_similarity_matrix(subnet_dir):
    """
    Load similarity matrix and CLid_to_index dict

    Parameters
    ----------
    subnet_dir:

    Output
    ------
    similarity_matrix, CLid_to_index

    >>> similarity_matrix, CLid_to_index = load_similarity_matrix(subnet_dir)
    """
    similarity_matrix = np.load(subnet_dir + 'cosine_sims.npy')

    with open(subnet_dir + 'CLid_to_index.p', 'rb') as f:
        CLid_to_index = pickle.load(f)

    return similarity_matrix.astype(np.float64), CLid_to_index


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
    # return [compute_similarity(tfidf_matrix, pair, CLid_to_index) for pair in CLid_pair]
    return [cosine_similarity(tfidf_matrix[CLid_to_index[pair[0]], :],
                              tfidf_matrix[CLid_to_index[pair[1]], :])[0][0]
            for pair in CLid_pair]
