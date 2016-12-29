import igraph as ig
import pandas as pd


def make_graph(experiment_data_dir, network_name=None):
    # load vertex metadata and edgelist
    case_metadata = pd.read_csv(experiment_data_dir + 'case_metadata.csv',
                                index_col=0)
    case_metadata.index = case_metadata.index.astype('str')

    edgelist = pd.read_csv(experiment_data_dir + 'edgelist.csv',
                           index_col=False)
    edgelist['citing'] = edgelist['citing'].astype(str)
    edgelist['cited'] = edgelist['cited'].astype(str)

    # initialize graph
    G = ig.Graph(n=case_metadata.shape[0], directed=True)

    # add opinion names
    G.vs['name'] = case_metadata.index

    # opinion to ig index mapping
    op_to_ig = {op_id: G.vs.find(name=op_id).index for op_id in G.vs['name']}

    # convert edgelist to ig ids
    edgelist_ig = edgelist.apply(lambda c: [op_to_ig[str(op_id)] for op_id in c])

    # add edes to graph
    G.add_edges(edgelist_ig.as_matrix().tolist())

    # add igraph index to case metadata
    case_metadata['ig_index'] = 0
    case_metadata.loc[G.vs['name'], 'ig_index'] = range(len(G.vs))

    # set missing issueArea to 0
    no_issueArea = case_metadata.index[case_metadata['issueArea'].isnull()]
    case_metadata.loc[no_issueArea, 'issueArea'] = 0
    case_metadata['issueArea'] = case_metadata['issueArea'].astype(int)

    # add year
    case_metadata['date'] = pd.to_datetime(case_metadata['date'])
    case_metadata['year'] = case_metadata['date'].apply(lambda d: d.year)

    # add node metadata to graph
    # pretty sure this is the right order
    G.vs['year'] = case_metadata['year']
    G.vs['issueArea'] = case_metadata['issueArea']
    G.vs['issueArea'] = case_metadata['issueArea']
    G.vs['court'] = case_metadata['court']

    # save graph
    if network_name:
        fname = network_name + '_network.graphml'
    else:
        fname = 'network.graphml'
    G.write_graphml(experiment_data_dir + fname)
