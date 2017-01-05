import numpy as np


def time_aware_pagerank(A, years, p, qtv, qvt):
    """
    Computes the time aware PageRank defined by the following random walk

    Create bi-partide time-node graph F
    - includes time as a node i.e. vertices are V(G) U V(G).years
    - F contains a copy of G
    - edge from each vetex to AND from its year
    - edges go from year to the following year

    When the random walk is at a vertex of G
    - probability qvt transitions to the time node
    - probability 1 - qvt does a PageRank move

    When the random walk is at a time node
    - probability qtv transitions to a vertex in G (of the corresponding year)
    - probability 1 - qtv moves to the next year

    Parameters
    ----------
    A: adjacency matrix of original matrix where Aij = 1
    iff there is an edge from i to j

    Y: the years assigned to each node

    p: PageRank parameter

    qtv: probability of transitioning from time to vertex in original graph

    qvt: probability of transitioning from vertx to time

    Output
    ------

    """
    # number of vertices in the graph
    n = A.shape[0]
    outdegrees = A.sum(axis=1)

    # zero index the years
    Y = np.array(years) - min(years)

    # number of years in graph
    m = max(Y) + 1

    # PageRank transition matrix
    # (see murphy 17.37)
    D = np.diag([0 if d == 0 else 1.0/d for d in outdegrees])
    z = [1.0/n if d == 0 else (1.0 - p) / n for d in outdegrees]
    PR = p * np.dot(A.T, D) + np.outer([1] * n, z)

    # Time-Time transition matrix
    # ones below diagonal
    TT = np.zeros((m, m))
    TT[1:m, :m-1] = np.diag([1] * (m - 1))

    # Vertex-Time transition matrix
    # i-th column is the Y[i]th basis vector
    VT = np.zeros((m, n))
    identity_m = np.eye(m)  # for basis vectors
    for i in range(n):
        VT[:, i] = identity_m[:, Y[i]]

    # Time-Vertex transition matrix
    # VT transpose but entries are scaled by number of cases in the year
    TV = np.zeros((n, m))
    # 1 over number of cases per year
    n_inv = [0 if cases_per_year[i] == 0 else 1.0/cases_per_year[i]
             for i in range(m)]
    for i in range(n):
        TV[i, :] = identity_m[Y[i], :] * n_inv[Y[i]]

    # normalization matrix for TV
    qtv_diag = [0 if cases_per_year[i] == 0 else qtv for i in range(m)]
    qtv_diag[-1] = 1  # last column of TT is zeros
    Qtv = np.diag(qtv_diag)

    # overall transition matrix
    P = np.zeros((n + m, n + m))
    P[:n, :n] = (1 - qvt) * PR  # upper left
    P[:n, -m:] = np.dot(TV, Qtv)  # upper right
    P[n:, :-m] = qvt * VT  # lower left
    P[-m:, -m:] = np.dot(TT, np.eye(m) - Qtv)  # lower right

    # get PageRank values
    leading_eig = get_leading_evector(P)
    ta_pr = leading_eig[:n]
    pr_years = leading_eig[-m:]

    # normalize to probabilty vectors
    return ta_pr/sum(ta_pr), pr_years/sum(pr_years)


def get_leading_evector(M):
    evals, evecs = np.linalg.eig(M)

    # there really has to be a more elegant way to do this
    return np.real(evecs[:, np.argmax(evals)].reshape(-1))
