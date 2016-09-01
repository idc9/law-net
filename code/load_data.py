import pandas as pd
import networkx as nx
import os

from download_data import url_to_dict


def get_network(case_metadata, edgelist):
    G = nx.DiGraph()
    G.add_nodes_from(case_metadata.index.tolist())
    for index, edge in edgelist.iterrows():
        ing = edge['citing']
        ed = edge['cited']

        G.add_edge(ing, ed)
    return G


def load_citation_network(data_dir, network):
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
    jurisdictions = pd.read_csv(data_dir + 'clean/jurisdictions.csv',
                                index_col='court')

    all_courts = set(jurisdictions.index)
    if (network not in all_courts) or (network != 'all'):
        raise ValueError('invalid network')

    if network == 'all':
        case_meatadata = pd.read_csv(data_dir + '/case_metadata_master.csv',
                                     index_col='id')

        edgelist = pd.read_csv(data_dir + 'clean/edgelist_master.csv')
    else:
        net_dir = data_dir + 'clean/' + network + '/'
        if not os.path.exists(net_dir):
            make_court_subnetwork(court_name, data_dir)

        case_meatadata = pd.read_csv(net_dir + '/case_metadata.csv',
                                     index_col='id')

        edgelist = pd.read_csv(net_dir + 'clean/edgelist.csv')

    G = nx.DiGraph()
    G.add_nodes_from(case_metadata.index.tolist())
    for index, edge in edgelist.iterrows():
        ing = edge['citing']
        ed = edge['cited']

        G.add_edge(ing, ed)

    return G


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

    pass


def case_info(case_id):
    """
    Given the case id returns a link to the opinion file on court listener
    """
    url = 'https://www.courtlistener.com/api/rest/v3/clusters/%s/?format=json'\
          % case_id

    case = url_to_dict(url)
    courtlistener_url = 'https://www.courtlistener.com/'
    opinion_url = courtlistener_url + case['absolute_url']

    print case['case_name']
    print case['date_filed']
    print
    print opinion_url
    print


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
