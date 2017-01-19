import numpy as np
import igraph as ig


def get_CiteRank(G, half_life, p=.85):
    """
    Retuns the CiteRank of a graph
    (see https://arxiv.org/pdf/physics/0612122.pdf)

    CiteRank is a particular PersonalizedPage rank where the reset
    probabilities exponentially decay with age of the vertex.

    Parameters
    ----------
    G: igraph graph, assumes 'year' is a vertex atttribute

    half_life: the half life of the exponential decay i.e.
    reset_prob_i propto 2^(- age_i / half_life)

    Returns
    -------
    CiteRank
    """

    # years of each case
    years = np.array(G.vs['year'])
    current_year = max(years)

    # compute exponentially decaying probabilities
    ages = current_year - years
    exp_weights = 2 ** (- ages/float(half_life))
    probs = exp_weights / exp_weights.sum()

    return G.personalized_pagerank(damping=p, reset=probs)


def get_CiteRankPoly(G, exponent, p=.85):
    """
    Retuns the CiteRank of a graph
    (see https://arxiv.org/pdf/physics/0612122.pdf)

    CiteRank is a particular PersonalizedPage rank where the reset
    probabilities exponentially decay with age of the vertex.

    Parameters
    ----------
    G: igraph graph, assumes 'year' is a vertex atttribute

    exponent: the exponent of the decay i.e.
    reset_prob_i propto 1/(age + 1)^exponent

    Returns
    -------
    CiteRank
    """
    # years of each case
    years = np.array(G.vs['year'])
    current_year = max(years)

    # compute exponentially decaying probabilities
    ages = current_year - years
    weights = 1.0 / (1.0 + ages) ** exponent
    probs = weights / weights.sum()

    return G.personalized_pagerank(damping=p, reset=probs)


def get_recent_citations(G, current_year, threshold):
    """
    Number of citations in past T years

    Parameters
    ---------
    G: igraph object with 'year' vertex attributes

    current_year: current year

    threshold: how many years before to look

    Output
    ------
    Returns a list ordered by ig index of recent citations

    i.e. number citations that happend after current_year - threshold
    """
    threshold_year = current_year - threshold
    return [get_citations_upto_(v, threshold_year) for v in G.vs]


def get_citations_upto_(v, threshold_year):
    """
    Retunrs the recent citaions for a given vertex

    helper function for get_recent_citations

    Parameters
    ----------
    v: vertex object from igraph object

    threshold_year: get citations that happened after this year
    """
    return len([ing for ing in v.neighbors(mode="IN")
                if threshold_year <= ing['year']])


def get_reverse_graph(G):
    """
    Reverses the eges of a graph

    Paramters
    ---------
    G: the graph to reverse

    Output
    ------
    reversed graph (does not include any vertex attributes)
    """
    G_rev = ig.Graph(n=len(G.vs), directed=True)

    # get reversed edge list
    rev_EL = [(e[1], e[0]) for e in G.get_edgelist()]

    G_rev.add_edges(rev_EL)

    return G_rev
