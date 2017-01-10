import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy.stats import rankdata


def get_feature_transform(X, feature_transform=None):
    """
    Transforms featurs
    """
    if feature_transform == 'interaction':
        poly = PolynomialFeatures(2)
        poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
        return poly.fit_transform(X)

    elif feature_transform == 'poly2':
        poly = PolynomialFeatures(2)
        poly = PolynomialFeatures(degree=2, interaction_only=False, include_bias=False)
        return poly.fit_transform(X)

    else:
        return X


def fit_logreg(y_train, x_train, feature_transform=None):
    '''
    Fits our logistic regression model. Any data you need for logistic
    regression should be in the edge data frame

    might try statsmodels i.e. see
    http://blog.yhat.com/posts/logistic-regression-python-rodeo.html

    Parameters
    ------------
    y_train:
    x_train:
    feature_transform:

    Output
    ------
    returns a logistic regression object
    '''

    # initialize logistic regression model
    LogReg = LogisticRegression(solver='liblinear',
                                penalty='l2',  # stupid scikit requires penalty
                                C=100,
                                fit_intercept=True)

    # transform features
    x_train = get_feature_transform(x_train, feature_transform)

    # fit log reg
    LogReg.fit(x_train, y_train)
    return LogReg


def predict_logreg(LogReg, x_test, cited_cases, feature_transform=None):
    '''
    Returns predictions for log reg model

    Parameters
    ------------
    y_train:
    x_train:
    feature_transform:

    Output
    ------
    returns a logistic regression object
    '''

    ranking = pd.DataFrame(index=[e[1] for e in x_test.index])

    # tranform features
    x_test = get_feature_transform(x_test, feature_transform)

    # get predicted citation probabilities
    # which class??
    citation_index = np.where(LogReg.classes_ == 1)[0]
    ranking['pred_prob'] = LogReg.predict_proba(x_test)[:, citation_index]  # should this be 0 or 1??
    # round to 3 sig figs
    ranking['pred_prob'] = ranking['pred_prob'].apply(lambda x: round(x, 3))

    # add case ranking
    ranking['rank'] = np.floor(rankdata(-ranking['pred_prob'],
                                        method='average'))

    # add citaions
    ranking['is_edge'] = 0
    ranking.loc[cited_cases, 'is_edge'] = 1

    return ranking
