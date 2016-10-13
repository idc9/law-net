import numpy as np
from scipy import stats
import pandas as pd

import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde


def print_describe(values):
    des = stats.describe(values)
    print 'nobs: %d' % stats.describe(values).nobs
    print 'mean: %1.2f' % stats.describe(values).mean
    print 'median: %1.2f' % np.median(values)
    print 'min: %1.2f' % stats.describe(values).minmax[0]
    print 'max: %1.2f' % stats.describe(values).minmax[1]
    print 'variance: %1.2f' % stats.describe(values).variance
    print 'unique values %d' % len(set(values))


def plot_scores(scores, palette=None,
                start=1, n_comp=3, classes=None,
                title=''):
    """
    Plots the scores plots of a data frame where the rows are observations and
    the columns are featurs

    for PCA when X = U D V^t, scores = U * D = X * V

    """
    # TODO: add overall title
    start -= 1  # zero indexing

    if not palette:
        ptcolor = 'black'
    else:
        ptcolor = palette

    plt.figure(figsize=[5 * n_comp, 5 * n_comp])
    p = 1
    for i in range(start, start + n_comp):
        for j in range(start, start + n_comp):
            if i == j:
                plt.subplot(n_comp, n_comp, p)
                # plt.hist(U[i, :])
                plot_jitter_hist(scores[:, i],
                                 palette=palette, classes=classes)
                plt.ylabel('comp %d' % (j + 1))
            elif i < j:
                plt.subplot(n_comp, n_comp, p)
                plt.scatter(scores[:, j], scores[:, i],
                            color=ptcolor, alpha=.8)
                plt.xlabel('comp %d' % (j + 1))
                plt.ylabel('comp %d' % (i + 1))

            p += 1


def plot_jitter_hist(y, palette=None, classes=None):
    """
    Jitter plot histogram
    """
    n = len(y)
    if not palette:
        palette = ['red'] * n

    if classes and (set(classes) != set([0, 1])):
        raise ValueError('classes vector not in proper format')

    # plot the histogram of the points
    hist = plt.hist(y, alpha=.6, color='black')
    counts, bins = hist[0], hist[1]

    # show each individual point using a jitter plot
    jitter_y = np.percentile(counts, .25)
    plt.scatter(y, np.random.uniform(0, 1, n) + jitter_y,
                color=palette, zorder=2)

    plt.xlim([min(bins), max(bins)])
    plt.ylim([0, max(counts)])

    if classes:
        # grab points in each class
        y0 = [y[i] for i in range(n) if classes[i] == 0]
        y1 = [y[i] for i in range(n) if classes[i] == 1]

        # points where we evaluate the pdf of the kde
        p = np.linspace(min(bins), max(bins), 1000)

        # get guassian KDE of individual classes
        y0_kde = gaussian_kde(y0, bw_method='scott').pdf(p)
        y1_kde = gaussian_kde(y1, bw_method='scott').pdf(p)

        # rescale kde so that is height is displayed on the counts scale
        # * len(y0) / (len(y0) + len(y1)) # could scale by class sizes
        # * len(y1) / (len(y0) + len(y1))
        scale0 = (max(counts) / max(y0_kde)) * .75
        scale1 = (max(counts) / max(y1_kde)) * .75
        y0_kde_s = [v * scale0 for v in y0_kde]
        y1_kde_s = [v * scale1 for v in y1_kde]

        # plot the class specific kdf pdfs
        plt.plot(p, y0_kde_s, color='blue')
        plt.plot(p, y1_kde_s, color='red')


def plot_pairwise_scatter(X, Y):
    """
    Makes the pairwise scatter plots for two pandas data frames X, Y
    """
    xvars = X.columns.tolist()
    yvars = Y.columns.tolist()

    plt.figure(figsize=[6 * len(yvars), 6 * len(xvars)])
    p = 1
    for i in range(len(xvars)):
        for j in range(len(yvars)):

            # plt.figure(figsize=[6, 6])
            plt.subplot(len(xvars), len(yvars), p)

            p += 1

            xvar = xvars[i]
            yvar = yvars[j]
            df = pd.concat([X[xvar], Y[yvar]], axis=1)

            plt.scatter(df[xvar], df[yvar], color='black')
            plt.xlabel(xvar)
            plt.ylabel(yvar)

            corr_coef = df.corr(method='pearson').loc[xvar, yvar]

            plt.annotate('corr: %1.3f' % corr_coef,
                         xy=(0.8, 0.92),
                         xycoords='axes fraction',
                         color='red')


def plot_scatter_matrix(X):
    """
    Plots the scatter plot matrix for all variable in X, a pandas data frame

    """
    d = X.shape[1]
    cols = X.columns.tolist()

    plt.figure(figsize=[6 * d, 6 * d])
    p = 1
    for i in range(d):
        for j in range(d):
            if i == j:

                # histogram of ith variable
                var = cols[i]
                plt.subplot(d, d, p)
                plot_jitter_hist(X[var])
                plt.ylabel(var)
            elif i < j:
                xvar = cols[j]
                yvar = cols[i]

                # scatter plot of ith vs jth variable
                plt.subplot(d, d, p)
                plt.scatter(X[xvar], X[yvar], color='black', alpha=.7)
                plt.xlabel(xvar)
                plt.ylabel(yvar)
                plt.xlim(min(X[xvar]), max(X[xvar]))
                plt.ylim(min(X[yvar]), max(X[yvar]))

                # add correlation coefficient
                corr_coef = X.corr(method='pearson').loc[xvar, yvar]
                plt.annotate('corr: %1.3f' % corr_coef,
                             xy=(0.8, 0.92),
                             xycoords='axes fraction',
                             color='red')

            p += 1


def plot_individual_loadings(start, n_comp, V):
    """
    Plots the K loadings individually.

    Parameters
    ----------
    V: loadings matrix (i.e. columns of V are evecs of X^tX where X is
    the centered data matrix with rows as observations)

    start: loading number to start at
    n_comp: how many loadings to plot
    """
    n_comp = int(n_comp)
    start = int(start)

    plt.figure(figsize=[16, 8 * n_comp])
    k = 1
    for p in range(n_comp):

        i = start + p

        # soreted loadings
        plt.subplot(n_comp, 2, k)
        v = np.matrix(V)[:, i - 1].A1
        v.sort()

        plt.scatter(range(len(v)), v,
                    color='black',
                    marker='.')

        plt.xlabel('index rank')
        plt.xlim([0, len(v)])
        plt.ylabel('value')
        plt.title('sorted entries of pricipal direction %d' % i)

        # unsorted loadings
        plt.subplot(n_comp, 2, k+1)
        v = np.matrix(V)[:, i - 1].A1

        plt.scatter(range(len(v)), v,
                    color='black',
                    marker='.')

        plt.xlabel('index')
        plt.xlim([0, len(v)])
        plt.ylabel('value')
        plt.title('entries of pricipal direction %d' % i)

        k += 2


def plot_K_loadings(V, K):
    """
    Plots the first K loadings.

    Parameters
    ----------
    V: loadings matrix (i.e. columns of V are evecs of X^tX where X is
    the centered data matrix with rows as observations)

    K: number of ladings components to include
    """
    plt.figure(figsize=[20, 10])

    # unsorted
    plt.subplot(1, 2, 1)
    for i in range(K):
        v = np.matrix(V)[:, i].A1
        plt.plot(range(len(v)), v,
                 color='black',
                 alpha=.2)

    plt.xlabel('index')
    plt.xlim([0, len(v)])
    plt.ylabel('value')
    plt.title('first %d pricipal directions' % K)

    # sorted
    plt.subplot(1, 2, 2)
    for i in range(K):
        v = np.matrix(V)[:, i].A1
        v.sort()
        plt.plot(range(len(v)), v,
                 color='black',
                 alpha=.5)

    plt.xlabel('rank')
    plt.xlim([0, len(v)])
    plt.ylabel('value')
    plt.title('sorted first %d pricipal directions' % K)
