import pandas as pd
import networkx as nx
import os
import time
import igraph as ig

from pipeline.download_data import url_to_dict
from pipeline.make_clean_data import make_court_subnetwork


def load_citation_network(data_dir, court_name, directed=True):
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
    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
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


def load_citation_network_igraph(data_dir, court_name, directed=True):
    jurisdictions = pd.read_csv(data_dir + 'clean/jurisdictions.csv',
                                index_col='abbrev')

    all_courts = set(jurisdictions.index)
    if not((court_name in all_courts) or (court_name == 'all')):
        raise ValueError('invalid court_name')

    start = time.time()
    if court_name == 'all':
        case_metadata = pd.read_csv(data_dir + 'clean/case_metadata_master.csv')

        edgelist = pd.read_csv(data_dir + 'clean/edgelist_master.csv')
    else:
        net_dir = data_dir + 'clean/' + court_name + '/'
        if not os.path.exists(net_dir):
            os.makedirs(net_dir)
            make_court_subnetwork(court_name, data_dir)

        case_metadata = pd.read_csv(net_dir + 'case_metadata.csv')

        edgelist = pd.read_csv(net_dir + 'edgelist.csv')
        edgelist.drop('Unnamed: 0', inplace=True, axis=1)

    # create a dictonary that maps court listener ids to igraph ids
    cl_to_ig_id = {}
    cl_ids = case_metadata['id'].tolist()
    for i in range(case_metadata['id'].size):
        cl_to_ig_id[cl_ids[i]] = i

    # add nodes
    V = case_metadata.shape[0]
    g = ig.Graph(n=V, directed=directed)
    # g.vs['date'] = case_metadata['date'].tolist()
    g.vs['name'] = case_metadata['id'].tolist()

    # create igraph edgelist
    cases_w_metadata = set(cl_to_ig_id.keys())
    ig_edgelist = []
    missing_cases = 0
    start = time.time()
    for row in edgelist.itertuples():

        cl_ing = row[1]
        cl_ed = row[2]

        if (cl_ing in cases_w_metadata) and (cl_ed in cases_w_metadata):
            ing = cl_to_ig_id[cl_ing]
            ed = cl_to_ig_id[cl_ed]
        else:
            missing_cases += 0

        ig_edgelist.append((ing, ed))

    # add edges to graph
    g.add_edges(ig_edgelist)

    # add vertex attributes
    g.vs['court'] = case_metadata['court'].tolist()
    g.vs['year'] = [int(d.split('-')[0]) for d in case_metadata['date'].tolist()]

    end = time.time()
    g.simplify(multiple=True)

    print '%d seconds for %d edges' % (end - start, len(g.es))
    return g


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
