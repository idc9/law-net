import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import re
import glob


def make_tf_idf(text_dir, output_dir, min_df=0, max_df=1):
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

    # to load
    tfidf_matrix =
    load_sparse_csr(experiment_data_dir + 'tfidf_matrix')

    with open(experiment_data_dir + 'op_id_to_bow_id.p', 'rb') as f:
        op_id_to_bow_id = pickle.load(f)

    with open(experiment_data_dir + 'vocab.p', 'rb') as f:
        vocab = pickle.load(f)
    """

    # text files
    file_paths = glob.glob(text_dir + '*.txt')

    # iterator over textfiles
    tf_iter = textfile_iter(file_paths)

    # compute bag of words
    tfidf = TfidfVectorizer(min_df=min_df, max_df=max_df)
    tfidf_matrix = bag_of_words.fit_transform(tf_iter)

    # vocabulary
    vocab = tfidf.get_feature_names()

    # map from CL opinion ids to bow matix index
    op_id_to_tfidf_id = {re.search(r'(\d+)\.txt', file_paths[i]).group(1): i for
                         i in range(len(file_paths))}

    # save data
    save_sparse_csr(output_dir + 'tfidf_matrix', bow_matrix)

    with open(output_dir + 'op_id_to_bow_id.p', 'wb') as fp:
        pickle.dump(op_id_to_bow_id, fp)

    with open(output_dir + 'vocab.p', 'wb') as fp:
        pickle.dump(vocab, fp)


def make_bag_of_words(text_dir, min_df=0, max_df=1):
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
    load_sparse_csr(experiment_data_dir + 'bag_of_words_matrix')

    with open(experiment_data_dir + 'op_id_to_bow_id.p', 'rb') as f:
        op_id_to_bow_id = pickle.load(f)

    with open(experiment_data_dir + 'vocab.p', 'rb') as f:
        vocab = pickle.load(f)

    """

    # text files
    file_paths = glob.glob(text_dir + '*.txt')

    # iterator over textfiles
    tf_iter = textfile_iter(file_paths)

    # compute bag of words
    bag_of_words = CountVectorizer(min_df=min_df, max_df=max_df)
    bow_matrix = bag_of_words.fit_transform(tf_iter)

    # vocabulary
    vocab = bag_of_words.get_feature_names()

    # map from CL opinion ids to bow matix index
    op_id_to_bow_id = {re.search(r'(\d+)\.txt', file_paths[i]).group(1): i for
                       i in range(len(file_paths))}

    # save data
    save_sparse_csr(experiment_data_dir + 'bag_of_words_matrix', bow_matrix)

    with open(experiment_data_dir + 'op_id_to_bow_id.p', 'wb') as fp:
        pickle.dump(op_id_to_bow_id, fp)

    with open(experiment_data_dir + 'vocab.p', 'wb') as fp:
        pickle.dump(vocab, fp)


class textfile_iter:
    """
    Iterator that returns a cleaned textfile given a list of paths
    """
    def __init__(self, paths):
        self.i = 0
        self.paths = paths
        self.num_files = len(paths)

    def __iter__(self):
        return self

    def next(self):
        if self.i < self.num_files:
            text = open(self.paths[self.i], 'r').read()
            self.i += 1

            return text_normalization(text)

        else:
            raise StopIteration()
