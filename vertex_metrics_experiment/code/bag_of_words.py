import numpy as np
import pandas as pd
import re
import glob
import cPickle as pickle

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords


from text_normalization import *
from pipeline_helper_functions import save_sparse_csr, load_sparse_csr


def make_tf_idf(text_dir, output_dir):
    """
    computes the td-idf matrix of a corpus

    Paramters
    ---------
    text_dir: directory containing text files

    Output
    ------
    tfidf_matrix: CSR matrix containing the td-idf vectors

    vocab: list of the vocabulary (ordered by the dict keys)

    op_id_to_tfidf_id: maps CL opinon id to index (dict)
    """

    file_paths = glob.glob(text_dir + '*.txt')
    tf_iter = textfile_iter(file_paths)

    # stemmer and stop words
    stemmer = PorterStemmer()
    stop_words = stopwords.words("english")
    min_df = 1  # be careful about integer/float, see sklean documentation
    max_df = 1.0

    # stem stop words
    stop_words = [stemmer.stem(w) for w in stop_words]

    tfidf = TfidfVectorizer(min_df=min_df,
                            max_df=max_df,
                            tokenizer=StemTokenizer(stemmer),
                            stop_words=stop_words)

    tfidf_matrix = tfidf.fit_transform(tf_iter)

    # vocabulary
    vocab = tfidf.get_feature_names()

    # map from CL opinion ids to bow matix index
    op_id_to_bow_id = {re.search(r'(\d+)\.txt', file_paths[i]).group(1): i for
                       i in range(len(file_paths))}

    # save data
    save_sparse_csr(output_dir + 'tfidf_matrix', tfidf_matrix)

    with open(output_dir + 'op_id_to_bow_id.p', 'wb') as fp:
        pickle.dump(op_id_to_bow_id, fp)

    with open(output_dir + 'vocab.p', 'wb') as fp:
        pickle.dump(vocab, fp)


def load_tf_idf(nlp_dir):
    """
    tfidf_matrix, op_id_to_bow_id = load_tf_idf(nlp_dir)
    """
    tfidf_matrix = load_sparse_csr(nlp_dir + 'tfidf_matrix.npz')

    with open(nlp_dir + 'op_id_to_bow_id.p', 'rb') as f:
        op_id_to_bow_id = pickle.load(f)

    with open(nlp_dir + 'vocab.p', 'rb') as f:
        vocab = pickle.load(f)

    return tfidf_matrix, op_id_to_bow_id, vocab

def load_bow(nlp_dir):
    """
    bow_matrix, op_id_to_bow_id = load_bow(nlp_dir)
    """
    bow_matrix = load_sparse_csr(nlp_dir + 'bag_of_words_matrix.npz')

    with open(nlp_dir + 'op_id_to_bow_id.p', 'rb') as f:
        op_id_to_bow_id = pickle.load(f)

    with open(nlp_dir + 'vocab.p', 'rb') as f:
        vocab = pickle.load(f)

    return bow_matrix, op_id_to_bow_id, vocab

def make_bag_of_words(text_dir):
    """
    computes the td-idf matrix of a corpus

    Paramters
    ---------
    text_dir: directory containing text files

    Output
    ------
    bow_matrix: CSR matrix containing the TD counts

    vocab: list of the vocabulary (ordered by the dict keys)

    op_id_to_bow_id: maps CL opinion id to bag of words index (dict)

    # to load
    bow_matrix_matrix =
    load_sparse_csr(subnet_dir + 'bag_of_words_matrix')

    with open(subnet_dir + 'op_id_to_bow_id.p', 'rb') as f:
        op_id_to_bow_id = pickle.load(f)

    with open(subnet_dir + 'vocab.p', 'rb') as f:
        vocab = pickle.load(f)

    """

    file_paths = glob.glob(text_dir + '*.txt')
    tf_iter = textfile_iter(file_paths)

    # stemmer and stop words
    stemmer = PorterStemmer()
    stop_words = stopwords.words("english")
    min_df = 1  # be careful about integer/float, see sklean documentation
    max_df = 1.0

    # stem stop words
    stop_words = [stemmer.stem(w) for w in stop_words]

    bag_of_words = CountVectorizer(min_df=min_df,
                                   max_df=max_df,
                                   tokenizer=StemTokenizer(stemmer),
                                   stop_words=stop_words)

    bow_matrix = bag_of_words.fit_transform(tf_iter)
    # vocabulary
    vocab = bag_of_words.get_feature_names()

    # map from CL opinion ids to bow matix index
    op_id_to_bow_id = {re.search(r'(\d+)\.txt', file_paths[i]).group(1): i for
                       i in range(len(file_paths))}

    # save data
    save_sparse_csr(subnet_dir + 'bag_of_words_matrix', bow_matrix)

    with open(subnet_dir + 'op_id_to_bow_id.p', 'wb') as fp:
        pickle.dump(op_id_to_bow_id, fp)

    with open(subnet_dir + 'vocab.p', 'wb') as fp:
        pickle.dump(vocab, fp)


class textfile_iter:
    """
    Iterator that returns a cleaned textfile given a list of paths
    """
    def __init__(self, paths):
        self.i = 0

        # if there is only one file
        if type(paths) == str:
            paths = [paths]

        self.paths = paths
        self.num_files = len(paths)

    def __iter__(self):
        return self

    def next(self):
        if self.i < self.num_files:
            text = open(self.paths[self.i], 'r').read()
            self.i += 1

            return text

        else:
            raise StopIteration()


def compute_similarities(op_ids_A, op_ids_B,
                         tfidf_matrix, op_id_to_bow_id):
    """
    Computes the similarities between pairs of cases. Function is written
    to take advantage of sklean's cosine_similarity funcion.

    Parameters
    ----------
    op_ids_A, op_ids_B: lists of opinon ids

    tfidf_matrix: precomputed tf-idf matrix

    op_id_to_bow_id: maps opinion id to tf-idf matrx index

    Output
    ------
    list of similarities
    """
    if len(op_ids_A) != len(op_ids_B):
        raise ValueError('lists not same length')

    # the left list is the shorter of the two lists
    if len(set(op_ids_A)) < len(set(op_ids_B)):
        left = op_ids_A
        right = op_ids_B
    else:
        left = op_ids_B
        right = op_ids_A

    # Series indexed by case pairs holding the computed similarities
    similarities = pd.Series(0, index=zip(left, right))

    # dictionary mapping one left document to corresponding right documents
    left_to_right = {op_id: [] for op_id in set(left)}
    for i in range(len(left)):
        left_to_right[left[i]].append(right[i])

    # for each left case compute the similarities for each right case
    for l in left_to_right.keys():

        # right cases corresponding to left case
        R = left_to_right[l]

        # X is a single vector
        X = tfidf_matrix[op_id_to_bow_id[l], :]

        # Y a matrix (rows corresponding to right cases)
        Y = tfidf_matrix[[op_id_to_bow_id[r] for r in R], :]

        # use scipy to cmpute the cosine similarities
        sims = cosine_similarity(X, Y)[0]

        # update similarity Series
        pairs_to_add = zip([l]*len(R) , R)
        similarities[pairs_to_add] = sims

    return similarities.tolist()
