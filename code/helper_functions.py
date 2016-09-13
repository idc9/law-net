import pandas as pd
import numpy as np
import warnings

def get_pairs(X):
    """
    Given a list NX returns a list of the
    len(X) choose 2 pairs
    """
    pairs = []
    for i in range(len(X)):
        for j in range(len(X)):
            if i < j:
                pairs.append((X[i], X[j]))
    return pairs


def print_full(x, columns=None):
    pd.set_option('display.max_rows', len(x))
    if columns:
        print x[columns]
    else:
        print(x)
    pd.reset_option('display.max_rows')


def upper_trimed_mean(x, alpha):
    """
    Removes alpha percent of the larges x values then takes the mean
    """
    n = len(x)
    n_trunc = int(alpha * n)

    if n == 0:
        warnings.warn('empty vector')
        return 0

    if len(x[-n_trunc:]) == 0:
        warnings.warn('over trimming')
        return np.mean(x)

    return np.mean(sorted(x)[-n_trunc:])
