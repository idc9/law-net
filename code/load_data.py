import pandas as pd


def load_citation_network(data_dir, network, directed=True):
    """
    Loads the citation subnetwork into networkx

    Parameters
    ----------
    data_dir: path to data directory

    network: which subnetwork i.e. fisc, scotus, etc
    'entire' gets the entire network

    metadata: which metadata to load

    directed: are the edges directed
    """
    pass


def load_jurisdiction_network(data_dir):
    """
    Loads the jurisdiction network into networkx

    Parameters
    ----------
    data_dir: path to data directory

    network: which subnetwork i.e. fisc, scotus, etc
    'entire' gets the entire network

    metadata: which metadata to load

    multi: if True then edges are directed, there can be self loops

    weighted: binary edge weights or counts of citations
    """

    jurisdictions = pd.read_csv(data_dir + 'clean/jurisdictions.csv',
                                index_col='Abbrev')

    case_meatadata = pd.read_csv(data_dir + 'clean/case_metadata_master.csv',
                                 index_col='id')

    edgelist = pd.read_csv(data_dir + 'clean/edgelist_master.csv')


# def load_jurisdictions(data_dir):
#     """
#     load the juridictions
#     """
#     jurisdictions = pd.read_csv(data_dir + 'clean/jurisdictions.csv')
#
#     # reindex by abbrev
#     jurisdictions.set_index('abbrev', drop=True, inplace=True)
#     jurisdictions.index.name = 'abbrev'
#
#     return jurisdictions
