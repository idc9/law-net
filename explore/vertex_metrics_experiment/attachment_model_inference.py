from sklearn.linear_model import LogisticRegression
import pandas as pd


def fit_logistic_regression(experiment_data_dir, columns_to_use):
    '''
    Fits our logistic regression model. Any data you need for logistic
    regression should be in the edge data frame

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
    df = pd.read_csv(path_to_edge_data_frame, index_col=0)
    y_train = df['edge']
    x_train = df[columns_to_use]

    # fit logistic regression model
    LogReg = LogisticRegression(solver='newton-cg')
    LogReg.fit(x_train, y_train)
    return LogReg
