import numpy as np
from scipy import stats
import pandas as pd

from sklearn.cross_decomposition import PLSRegression


def standardize_vector(v, center=True, scale=False):
    if center:
        v = v - np.mean(v)

    if scale:
        if np.std(v) == 0:
            return v
        else:
            return (v + 0.0) / np.std(v)


def standardize_vec(v, center='mean', scale='std'):
    """"
    Standardizes a vector by centering and scaling it

    This function will ignore scaling if the scale value is zero and will
    instead set the scale value to 1
    """
    # choose the center value
    if not center:
        cent_val = 0.0
    elif center == 'mean':
        cent_val = np.mean(v)
    elif center == 'median':
        cent_val = np.median(v)
    elif type(center) in [float, int]:
        cent_val = center
    else:
        raise ValueError('improper center value')

    # choose the scale value
    if not scale:
        scale = 1.0
    elif scale == 'max':
        scale_val = max(v)
    elif scale == 'std':
        scale_val = np.std(v)
    elif scale == 'mean':
        scale_val = np.mean(v)
    elif scale == 'median':
        scale_val = np.median(v)
    elif type(scale) in [float, int]:
        scale_val = scale
    else:
        raise ValueError('improper scale value')

    # don't scale if scale value is zero
    if scale_val == 0:
        scale_val = 1

    return (v - cent_val + 0.0) / scale_val


def get_PCA(X, scale=False):
    """
    Returns the PCA decomposition of data frame X.
    Rows of X are observations and columns are features.
    Centers columns then performs PCA.

    Optionally scales columns by standard deviation

    X = U D V^t

    Output
    ------
    U, D, V

    """
    # center columns
    X_stand = X.apply(lambda c: standardize_vector(c,
                                                   center=True, scale=scale))

    # do SVD
    return np.linalg.svd(X_stand, full_matrices=False)


def get_pls(X, Y, n_comp):
    """
    returns the PLS scores

    parameters
    ----------
    X: pandas data frame
    Y: list
    """

    # center and scale both X and y data
    x = np.array(X.apply(lambda c: standardize_vector(c, center=True,
                                                      scale=True)))
    y = standardize_vector(Y, center=True, scale=True)

    # compute PLS direcections
    pls = PLSRegression(n_components=int(n_comp), scale=True)
    pls.fit(x, y)

    return np.array(pls.x_scores_), pls.x_loadings_
