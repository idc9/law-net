

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
