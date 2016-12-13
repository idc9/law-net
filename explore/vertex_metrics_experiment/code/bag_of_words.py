import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


def get_td_idf(normalized_text_dict):
    """
    computes the td-idf matrix of a corpus

    Paramters
    ---------
    normalized_text_dict: dictionary containing the corpus
    keys should be names of corpus documents

    Output
    ------
    tfidf_matrix: CSR matrix containing the td-idf vectors

    vocab: list of the vocabulary (ordered by the dict keys)

    CLid_to_index: maps CL id to index (dict)
    """
    # initialize tdidf vectorizer
    tfidf = TfidfVectorizer()

    # rows are documents (ordered by token_dict.keys())
    # columns are tersm (ordered by vocab below)
    tfidf_matrix = tfidf.fit_transform(normalized_text_dict.values())

    # document vocabulary
    vocab = tfidf.get_feature_names()

    # map CL ids to index of tf-idf matrix
    cases = normalized_text_dict.keys()
    CLid_to_index = {cases[i]: i for i in range(len(cases))}

    return tfidf_matrix, vocab, CLid_to_index


def get_bag_of_words(normalized_text_dict):
    """
    computes the td-idf matrix of a corpus

    Paramters
    ---------
    normalized_text_dict: dictionary containing the corpus
    keys should be names of corpus documents

    Output
    ------
    bow_matrix: CSR matrix containing the TD counts

    vocab: list of the vocabulary (ordered by the dict keys)

    CLid_to_index: maps CL id to index (dict)
    """
    # initialize tdidf vectorizer
    bow_counter = CountVectorizer()

    # rows are documents (ordered by token_dict.keys())
    # columns are tersm (ordered by vocab below)
    bow_matrix = bow_counter.fit_transform(normalized_text_dict.values())

    # document vocabulary
    vocab = bow_counter.get_feature_names()

    # map CL ids to index of tf-idf matrix
    cases = normalized_text_dict.keys()
    CLid_to_index = {cases[i]: i for i in range(len(cases))}

    return bow_matrix, vocab, CLid_to_index
