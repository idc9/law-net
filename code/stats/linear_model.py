import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import statsmodels.api as sm


def get_SLR(X, Y, to_plot=True, xlabel='', ylabel=''):
    """
    Plots LS fit for Simple Linear Regression
    Parameters
    ----------
    X, Y: regression variables (lists)
    Output
    ------
    plot: scatter plot of data with regression line.
    P value for H0: beta = 0 and Rsq printed on plot
    """

    # set up data frame
    df = pd.DataFrame(columns=['X', 'Y'])
    df['X'] = X
    df['Y'] = Y
    df = sm.add_constant(df)

    lm_fit = sm.OLS(df['Y'], df.drop('Y', 1)).fit()

    if to_plot:
        print lm_fit.summary()

        # add points
        plt.figure(figsize=[8, 8])
        plt.scatter(df['X'], df['Y'])
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        # x/y range (slighly larger than)
        min_x = min(df['X']) - .01 * abs(min(df['X']))
        max_x = max(df['X']) + .01 * abs(max(df['X']))
        min_y = min(df['Y']) - .01 * abs(min(df['Y']))
        max_y = max(df['Y']) + .01 * abs(max(df['Y']))

        plt.xlim([min_x, max_x])
        plt.ylim([min_y, max_y])

        # add linear regression line
        plt.plot([min_x, max_x],
                 lm_fit.predict(sm.add_constant([min_x, max_x])),
                 color='red',
                 linewidth=3)

        # add p value for beta = 0 and Rsq to plot
        p_val = lm_fit.pvalues['X']
        if p_val < 0.05:
            p_fontweight = 'bold'
        else:
            p_fontweight = 'normal'

        Rsq = lm_fit.rsquared

        plt.annotate('p_val: %1.3f' % p_val,
                     xy=(0.75, .95),
                     xycoords='axes fraction',
                     color='red',
                     size=15,
                     fontweight=p_fontweight,
                     zorder=3)

        plt.annotate('Rsq: %1.3f' % Rsq,
                     xy=(0.75, 0.9),
                     xycoords='axes fraction',
                     color='red',
                     size=15,
                     zorder=3)

    return lm_fit
