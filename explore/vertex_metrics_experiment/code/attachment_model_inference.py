from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np


def fit_logistic_regression(experiment_data_dir, columns_to_use):
    '''
    Fits our logistic regression model. Any data you need for logistic
    regression should be in the edge data frame

    might try statsmodels i.e. see
    http://blog.yhat.com/posts/logistic-regression-python-rodeo.html

    Parameters
    ------------
    experiment_data_dir:

    columns_to_use: list of column names of edge metrics data frame that
    we should use to fit logistic regression

    Output
    ------
    returns a logistic regression object
    '''
    # set up training data
    path_to_edge_data_frame = experiment_data_dir + 'edge_data.csv'
    df = pd.read_csv(path_to_edge_data_frame)
    y_train = df['is_edge']
    x_train = df[columns_to_use]

    # fit logistic regression model
    LogReg = LogisticRegression(solver='liblinear',
                                penalty='l2',  # stupid scikit requires penalty
                                C=100,
                                fit_intercept=True)

    LogReg.fit(x_train, y_train)
    return LogReg
