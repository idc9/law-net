import pandas as pd
import numpy as np
import warnings
from scipy.stats import rankdata
from datetime import datetime
import time
from math import *


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


def rankdata_reverse(x):
    """
    returns the ranks of data if large numbers are good i.e.

    >>> rankdata_reverse([3, 2, 1])
    >>> 1, 2, 3
    """
    return rankdata([-v for v in x], method='min')


def print_progress(current, maybe_print=False, outof=None,
                   current_time=False, start_time=None):
    """
    Prints the progress of a loop

    Parameters
    ----------
    maybe_print: wether or not to print progres
    outof: total number of iterations
    current_time: print the current time or not
    start_time: start time from time.time()
    """
    if maybe_print:
        # check if current is power of two
        if current == 0:
            log_2 = 0
        else:
            log_2 = log(current, 2)

        if int(log_2) == log_2:  # if power of two
            if outof:
                progress_string = '(%d/%d) ' % (current, outof)
            else:
                progress_string = str(current)

            if current_time:
                progress_string += ' %s' % datetime.now().strftime('%H:%M:%S %m-%d ')

            print progress_string

            if start_time:
                print '%d seconds since start' % (time.time() - start_time)
                print
