import numpy as np
import scipy as sp


def get_mean_rankscore(relevant, ranking):
    """
    Retuns the mean rank score for a ranking.
    The rank score of a ranked case is defined to be

    rank_score = rank/num_ancestors

    the mean rank score is the mean of all the rank scores of the cited cases

    Between 0 and 1. Smaller values are better. Random ranking is .5.

    See Zanin et al. (pref attachemnt aging ...)

    Parameters
    ----------
    R: list of cases that were cited

    ranking: ranking of ancestors

    Output
    ------
    average of cited case ranks scores scores
    """

    rank_scores = []

    # number of ancestors
    num_items = ranking.shape[0]

    # compute rank score for each case test case actually cited
    for r in relevant:

        # where cited case was ranked ()
        rank = get_rank(r, ranking)

        # score the ranking
        rank_score = float(rank) / num_items

        rank_scores.append(rank_score)

    # return np.mean(rank_scores)
    return np.nanmean(rank_scores)


def get_reciprocal_rank(relevant, ranking):
    """
    Returns the reciprocal rank 1 / r(c) where r(c)
    is the rank of the best rank of the cited cases.

    Between 0 and 1, smaller is better

    Parameters
    ----------
    relevant: list of cases that were cited

    ranking: ranking of ancestors

    Output
    ------
    reciprocal rank
    """

    ranks = []

    # compute rank score for each case test case actually cited
    for r in relevant:

        # where cited case was ranked ()
        rank = get_rank(r, ranking)

        ranks.append(rank)

    return 1.0/min(ranks)


def get_precision_at_K(relevant, ranking, K):
    """
    Returns the precision at K
    P@K = num cited cases in top K poisitions of ranking / K


    Parameters
    ----------
    relevant: list of cases that were cited

    ranking: ranking of ancestors

    Output
    ------
    precision at K
    """

    # get top k ranked cases
    top_k = set(ranking[ranking['rank'] <= K].index)
    precision_k = [1 for r in relevant if r in top_k]

    return float(len(precision_k)) / K


def get_rank(case, ranking):
    """
    either returns the rank or np.nan
    """
    try:
        return ranking.loc[case, 'rank']
    except Exception:
        return np.nan


def get_error_rate(predictions):
    """
    Returns the erro 0-1 classification prediction

    Parameters
    ----------
    predictions: pd df with columns 'pred_prob' and 'y'
    """

    cutoff = 0.5
    # get list of predicted probs and citaiton indicators
    y_act = predictions['is_edge'].tolist()
    y_pred = [1 if p > cutoff else 0 for p in predictions['pred_prob']]

    return np.mean([1 if y_act[i] == y_pred[i] else 0
                    for i in range(len(y_act))])


def get_logloss(predictions):
    """
    Returns the log-loss for a 0-1 classification predictions

    Parameters
    ----------
    predictions: pd df with columns 'pred_prob' and 'y'
    """

    # get list of predicted probs and citaiton indicators
    y_act = predictions['is_edge'].tolist()
    prob = predictions['pred_prob'].tolist()

    return logloss(y_act, prob)


def logloss(act, pred):
    """
    Returns the log loss

    Parameters
    ----------

    """
    epsilon = 1e-15
    pred = sp.maximum(epsilon, pred)
    pred = sp.minimum(1-epsilon, pred)
    ll = sum(act*sp.log(pred) + sp.subtract(1, act)*sp.log(sp.subtract(1, pred)))
    ll = ll * -1.0/len(act)
    return ll
