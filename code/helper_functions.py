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
