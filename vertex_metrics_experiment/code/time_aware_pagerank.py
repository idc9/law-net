import numpy as np
from collections import Counter
from scipy.sparse import csr_matrix, dia_matrix
from numpy.linalg import norm

from math import sqrt


def get_time_aware_pagerank_matrix(A, years, p, qtv, qvt):
    """
    Returns the transition matrix of the time aware PageRank random walk
    defined as follows. This method does not take advantage of sparse matrices
    for intermediate computation.

    Create bipartide time-as-a-node graph F
    - include time as a node i.e. vertices are V(G) U V(G).years
    - F contains a copy of G
    - edge from each vetex to AND from its year
    - edges go from each year to the following year

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
    P: the transition matrix (columns sum to 1)
    """
    A = csr_matrix(A, dtype=int)

    # number of vertices in the graph
    n = A.shape[0]
    # surely there is a more elegant way to do this
    outdegrees = A.sum(axis=1).reshape(-1).tolist()[0]

    # zero index the years
    Y = np.array(years) - min(years)
    m = max(Y) + 1

    # number of cases per year
    cases_per_year = [0] * m
    cases_per_year_counter = Counter(Y)
    for k in cases_per_year_counter.keys():
        cases_per_year[k] = cases_per_year_counter[k]

    # PageRank transition matrix
    # (see murphy 17.37)
    D = csr_matrix(np.diag([0 if d == 0 else 1.0/d for d in outdegrees]))
    z = [1.0/n if d == 0 else (1.0 - p) / n for d in outdegrees]
    PR = (1 - qvt) * p * (A.transpose() * D)
    PR = PR.todense()
    PR = PR + np.outer([1 - qvt] * n, z)

    # Time-Time transition matrix
    # ones below diagonal
    TT = np.zeros((m, m))
    TT[1:m, :m-1] = np.diag([1] * (m - 1))
    TT = dia_matrix(TT)

    # Vertex-Time transition matrix
    # i-th column is the Y[i]th basis vector
    VT = np.zeros((m, n))
    identity_m = np.eye(m)  # for basis vectors
    for i in range(n):
        VT[:, i] = qvt * identity_m[:, Y[i]]

    # Time-Vertex transition matrix
    # VT transpose but entries are scaled by number of cases in the year
    TV = np.zeros((n, m))
    # 1 over number of cases per year
    n_inv = [0 if cases_per_year[i] == 0 else 1.0/cases_per_year[i]
             for i in range(m)]
    for i in range(n):
        TV[i, :] = identity_m[Y[i], :] * n_inv[Y[i]]
    TV = csr_matrix(TV)

    # normalization matrix for TV
    qtv_diag = [0 if cases_per_year[i] == 0 else qtv for i in range(m)]
    qtv_diag[-1] = 1  # last column of TT is zeros
    Qtv = csr_matrix(np.diag(qtv_diag))

    # overall transition matrix
    P = np.zeros((n + m, n + m))  # upper left
    P[:n, :n] = PR  # lower left
    P[n:, :-m] = VT  # upper right
    P[:n, -m:] = (TV * Qtv).todense()  # lower right
    P[-m:, -m:] = (TT * dia_matrix(np.eye(m) - Qtv)).todense()

    return P


def get_time_aware_pagerank(A, years, p, qtv, qvt):
    """
    Computes time aware page rank (see get_time_aware_pagerank_matrix for
    description).

    Parameters
    ----------
    A: adjacency matrix

    p, qtv, qvt: parameters (see helper function)

    solver: which solver to use. Options are 'linear', 'krylov' and 'eigen'
    """

    # compute the transition matrix
    P = get_time_aware_pagerank_matrix(A, years, p, qtv, qvt)

    # get steady state distribution
    steady_state = power_method(P)

    # separate vertices and time nodes
    n = A.shape[0]
    m = len(steady_state) - n
    ta_pr = steady_state[:n]
    pr_years = steady_state[-m:]

    # re-normalize to probabilty vectors
    return ta_pr/sum(ta_pr), pr_years/sum(pr_years)


def power_method(P, init=None, tol = 1e-8, maxiter = 1e5):
    """
    Borrowing form
    https://github.com/gvanderheide/discreteMarkovChain/blob/master/discreteMarkovChain/markovChain.py
    """
    size = P.shape[0]
    if init is None:
        pi = np.ones(size) / sqrt(size)
        # pi = np.zeros(size)
        # pi[0] = 1
    else:
        pi = init / norm(init)

    pi1 = np.zeros(size)

    diff = norm(pi - pi1,1)
    i = 0
    while diff > tol and i < maxiter:
        i +=1

        # update pi vector
        pi1 = np.dot(P, pi)
        pi = np.dot(P, pi1)

        # how much did pi change
        diff = norm(pi - pi1,1)

    return pi
