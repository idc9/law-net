from __future__ import division
import pandas as pd
import glob
import random as random
import copy

from pipeline_helper_functions import *


def make_edge_df(G, experiment_data_dir, snapshot_year_list,
                 num_non_edges_to_add, columns_to_use, seed=None):

    # load snapshot dataframes
    snapshots_dict = load_snapshots(experiment_data_dir, train=True)

    # similarity_matrix = pd.read_csv(experiment_data_dir + 'similarity_matrix.csv', index_col=0)
    similarity_matrix = 0

    # initialize edge data frame
    colnames = copy.deepcopy(columns_to_use)
    colnames.append('is_edge')
    edge_data = pd.DataFrame(columns=colnames)

    # get all present edges
    present_edgelist = G.get_edgelist()

    # organize edges by ing snapshot year
    edges_by_snap_year_dict = get_edges_by_snapshot_dict(G, present_edgelist,
                                                         snapshot_year_list)

    # add present edge data
    for sn_year in snapshot_year_list:
        # vertex metrcs in snapshot year
        snapshot_df = snapshots_dict['vertex_metrics_' + str(sn_year)]

        # edges to add whos ing year is in the snapshot year
        edges = edges_by_snap_year_dict[sn_year]

        # get snapshot year edge data frame
        sn_edge_data = get_edge_data(G, edges, snapshot_df,
                                     similarity_matrix, edge_status='present')
        edge_data = edge_data.append(sn_edge_data)

    # get a sample of non-present edges
    absent_edgelist = sample_non_edges(G, num_non_edges_to_add, seed=seed)

    # organize edges by ing snapshot year
    edges_by_snap_year_dict = get_edges_by_snapshot_dict(G, absent_edgelist,
                                                         snapshot_year_list)

    # add absent edge data
    for sn_year in snapshot_year_list:
        # vertex metrcs in snapshot year
        snapshot_df = snapshots_dict['vertex_metrics_' + str(sn_year)]

        # edges to add whos ing year is in the snapshot year
        edges = edges_by_snap_year_dict[sn_year]

        # get edge data frame for snapshot year
        sn_edge_data = get_edge_data(G, edges, snapshot_df,
                                     similarity_matrix, edge_status='absent')
        edge_data = edge_data.append(sn_edge_data)

    edge_data.to_csv(experiment_data_dir + 'edge_data.csv')


def get_edges_by_snapshot_dict(G, edgelist, snapshot_year_list):
    """
    Organizes edges by ing snapshot year

    """

    num_edges = len(edgelist)

    # get the citing year of each edge
    ing_years = [G.vs[edge[0]]['year'] for edge in edgelist]

    # map the citing year to the snapshot year
    snap_ing_years = [get_snapshot_year(y, snapshot_year_list)
                      for y in ing_years]

    # dict that organizes edges by ing snapshot year
    edges_by_ing_snap_year_dict = {y: [] for y in snapshot_year_list}
    for i in range(num_edges):
        sn_year = snap_ing_years[i]
        edge = edgelist[i]

        edges_by_ing_snap_year_dict[sn_year].append(edge)

    return edges_by_ing_snap_year_dict


def sample_non_edges(G, num_non_edges_to_add, seed=None):
    '''
    Samples a number of nonexistent edges from the network G

    Parameters
    ----------
    G: network

    year_interval: the year interval between each vertex metric .csv file

    num_non_edges_to_add: how many nonexistent edges to add

    Output
    --------
    List of non-present edges
    '''
    # TODO: make seed work for ranomd package
    if seed:
        np.random.seed(seed)  # set seed for random packakge!

    # set makes adding 'edge_tuple' unique in the while loop
    # (need b/c random sampling can return duplicates)
    non_edge_set = set([])
    edges = set(G.get_edgelist())  # set faster than list for searching
    vertices = set(G.vs)  # vertices to select from

    while len(non_edge_set) < num_non_edges_to_add:
        # get random_edge
        temp = random.sample(vertices, 2)  # default: without replacement
        random_edge = (temp[0].index, temp[1].index)

        # get info from edge
        citing_year = G.vs(random_edge[0])['year'][0]
        cited_year = G.vs(random_edge[1])['year'][0]

        # only add a random edge if the citing year is after the cited year,
        # if it is not a present edge, and if it is not already sampled
        if random_edge not in edges and citing_year >= cited_year and random_edge not in non_edge_set:
            # determine which vertex_df to retrieve
            non_edge_set.add(random_edge)

    return list(non_edge_set)
