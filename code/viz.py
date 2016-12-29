import numpy as np
from scipy import stats
import pandas as pd

import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde


def print_describe(values):
    print 'nobs: %d' % len(values)
    print 'mean: %1.3f' % np.mean(values)
    print 'median: %1.3f' % np.median(values)
    print 'min: %1.3f' % min(values)
    print 'max: %1.3f' % max(values)
    print 'std: %1.3f' % np.std(values)
    print 'unique values %d' % len(set(values))


def plot_scores(scores,
                start=1,
                n_comp=3,
                title='',
                labels=None):
    """
    Plots the scores plots of a data frame where the rows are observations and
    the columns are featurs

    for PCA when X = U D V^t, scores = U * D = X * V

    """
    # TODO: add overall title

    if type(scores) == pd.core.frame.DataFrame:
        labels = scores.columns.tolist()
        scores = scores.as_matrix()

    if labels is None or len(labels) < n_comp:
        lables = ['comp %d' % j for j in range(1, n_comp + 1)]

    start -= 1  # zero indexing

    plt.figure(figsize=[5 * n_comp, 5 * n_comp])
    plt.title(title)
    p = 1
    for i in range(start, start + n_comp):
        for j in range(start, start + n_comp):
            if i == j:
                plt.subplot(n_comp, n_comp, p)
                # plt.hist(U[i, :])
                plot_jitter_hist(scores[:, i])
                plt.ylabel(labels[j])
            elif i < j:
                plt.subplot(n_comp, n_comp, p)
                plt.scatter(scores[:, j], scores[:, i], alpha=.8)
                plt.xlabel(labels[j])
                plt.ylabel(labels[i])

                if i == 0 and j == 1:
                    plt.title(title)

            p += 1


def plot_jitter_hist(y, n_bins=10, xlabel='', title=''):
    """
    Jitter plot histogram
    """
    n = len(y)

    # plot the histogram of the points
    bins = np.linspace(min(y), max(y), n_bins)
    hist = plt.hist(y, bins=bins, alpha=.8, color='blue')
    counts, bins = hist[0], hist[1]

    # show each individual point using a jitter plot
    jitter_y = max(counts) * .1
    jitter_spread = max(counts) * .01
    jitters = np.random.uniform(low=-jitter_spread,
                                high=jitter_spread, size=n) + jitter_y
    plt.scatter(y, jitters,
                color='red', alpha=.7, zorder=2)

    plt.xlim([min(bins), max(bins)])
    plt.ylim([0, max(counts)])

    plt.xlabel(xlabel)
    plt.title(title)

    # # points where we evaluate the pdf of the kde
    # p = np.linspace(min(bins), max(bins), 1000)
    #
    # # get guassian KDE of individual classes
    # y_kde = gaussian_kde(y0, bw_method='scott').pdf(p)
    #
    # # plot the class specific kdf pdfs
    # plt.plot(p, y_kde, color='blue')



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
        v = np.matrix(V)[i - 1, :].A1
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
        v = np.matrix(V)[i, :].A1
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


def plot_2class_scores(scores, classes, start=0, n_comp=3):
    """
    creates scores plot with two classes
    """
    clA_label = list(set(classes))[0]
    clB_label = list(set(classes))[1]

    palette = class_pallette = ['blue' if c == clA_label
                                else 'red' for c in classes]

    plt.figure(figsize=[5 * n_comp, 5 * n_comp])
    p = 1
    for i in range(start, start + n_comp):
        for j in range(start, start + n_comp):
            if i == j:
                plt.subplot(n_comp, n_comp, p)
                plot_2class_hist(scores[:, i], classes,
                                 legend=(p == 1),
                                 xlabel='comp %d' % (j + 1))

            elif i < j:
                plt.subplot(n_comp, n_comp, p)
                plt.scatter(scores[:, j], scores[:, i],
                            color=palette, alpha=.8)
                plt.xlabel('comp %d' % (j + 1))
                plt.ylabel('comp %d' % (i + 1))
            p += 1


def plot_2class_hist(X, classes, legend=True, xlabel=''):

    clA_label = list(set(classes))[0]
    clB_label = list(set(classes))[1]

    palette = class_pallette = ['blue' if c == clA_label
                                else 'red' for c in classes]

    # plot the histogram of the points
    hist = plt.hist(X, alpha=.6, color='black')
    counts, bins = hist[0], hist[1]

    # show each individual point using a jitter plot
    jitter_y = np.percentile(counts, .25)
    plt.scatter(X, np.random.uniform(0, 1, len(X)) + jitter_y,
                color=palette, zorder=2)

    plt.xlim([min(bins), max(bins)])
    plt.ylim([0, max(counts)])
    plt.y

    # grab points in each class
    Xa = [X[k] for k in range(len(X)) if classes[k] == clA_label]
    Xb = [X[k] for k in range(len(X)) if classes[k] == clB_label]

    # points where we evaluate the pdf of the kde
    pts = np.linspace(min(bins), max(bins), 1000)

    # get guassian KDE of individual classes
    Xa_kde = gaussian_kde(Xa, bw_method='scott').pdf(pts)
    Xb_kde = gaussian_kde(Xb, bw_method='scott').pdf(pts)

    # rescale kde so that is height is displayed on the countsscale
    # * len(y0) / (len(y0) + len(y1)) # could scale by class sizes
    # * len(y1) / (len(y0) + len(y1))
    scale0 = (max(counts) / max(Xa_kde)) * .75
    scale1 = (max(counts) / max(Xb_kde)) * .75
    Xa_kde_s = [v * scale0 for v in Xa_kde]
    Xb_kde_s = [v * scale1 for v in Xb_kde]

    # plot the class specific kdf pdfs
    plt.plot(pts, Xa_kde_s, color='blue', label=clA_label)
    plt.plot(pts, Xb_kde_s, color='red', label=clB_label)

    if legend:
        plt.legend(loc='upper right')


def get_jitter(N, base, width):
    return base + np.random.uniform(low=-width, high=width, size=N)
