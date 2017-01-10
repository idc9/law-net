import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def plot_scores(results, exper='', metric='', network_name=''):
    """
    plots the results
    """
    # compute mean and std of data
    data = pd.DataFrame(index=results.columns, columns=['score', 'error'])
    data['score'] = results.median(axis=0)
    data['error'] = results.std(axis=0)
    data.sort_values(by='score', inplace=True)

    # label locations
    pos = np.arange(data.shape[0])

    # configure error bars
    error_config = {'ecolor': 'red',
                    'alpha': .5}
    plt.barh(pos,
             data['score'],
             color='blue',
             alpha=.5,
             xerr=data['error'],
             error_kw=error_config)

    plt.xlim([0, 1.2 * data['score'].max()])

    # add labels
    plt.yticks(pos, data.index)

    plt.title('%s experiment, %s' % (exper, network_name))
    plt.xlabel(metric)


def get_year_aggregate(years, x, fcn):

    by_year = {y: [] for y in set(years)}
    for i in range(len(years)):
        by_year[years[i]].append(x[i])

    year_agg_dict = {y: fcn(by_year[y]) for y in by_year.keys()}
    return pd.Series(year_agg_dict)
