import pandas as pd
import networkx as nx
import os

from pipeline.download_data import url_to_dict
from pipeline.make_clean_data import make_court_subnetwork


def load_citation_network(data_dir, court_name):
    """
    Loads the citation subnetwork into networkx

    Parameters
    ----------
    data_dir: path to data directory

    court_name: which subnetwork i.e. fisc, scotus, etc
    'entire' gets the entire network

    metadata: which metadata to load

    directed: are the edges directed
    """
    jurisdictions = pd.read_csv(data_dir + 'clean/jurisdictions.csv',
                                index_col='abbrev')

    all_courts = set(jurisdictions.index)
    if not((court_name in all_courts) or (court_name == 'all')):
        raise ValueError('invalid court_name')

    if court_name == 'all':
        case_metadata = pd.read_csv(data_dir + 'clean/case_metadata_master.csv',
                                    index_col='id')

        edgelist = pd.read_csv(data_dir + 'clean/edgelist_master.csv')
    else:
        net_dir = data_dir + 'clean/' + court_name + '/'
        if not os.path.exists(net_dir):
            os.makedirs(net_dir)
            make_court_subnetwork(court_name, data_dir)

        case_metadata = pd.read_csv(net_dir + 'case_metadata.csv',
                                    index_col='id')

        edgelist = pd.read_csv(net_dir + 'edgelist.csv')

    # create graph and add metadata
    G = nx.DiGraph()
    G.add_nodes_from(case_metadata.index.tolist())
    nx.set_node_attributes(G, 'date', case_metadata['date'].to_dict())
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
    """

    pass


def case_info(case_id):
    """
    Given the case id returns a link to the opinion file on court listener
    """
    url = 'https://www.courtlistener.com/api/rest/v3/clusters/%s/?format=json'\
          % case_id

    case = url_to_dict(url)
    courtlistener_url = 'https://www.courtlistener.com'
    opinion_url = courtlistener_url + case['absolute_url']

    print case['case_name']
    print case['date_filed']
    print
    print opinion_url
    print
