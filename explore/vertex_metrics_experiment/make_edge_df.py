from __future__ import division
import pandas as pd
import glob
import random as random

from pipeline_helper_functions import *


def get_snapshot_edge_metrics_dep(G, experiment_data_dir,
                              year_interval,
                              num_non_edges_to_add,
                              seed=None):

    snapshots_dict = load_snapshots(experiment_data_dir, train=True)

    # list of edges that will be added to the edge df
    edgedata_list = []

    # get all present edges
    edgelist_to_add = G.get_edgelist()
    fill_edgedata_list(edgedata_list, G, edgelist_to_add, year_interval,
                       snapshots_dict, edges_exist=True)

    # get a sample of non-present edges
    nonedges_to_add = sample_non_edges(G, year_interval, num_non_edges_to_add,
                                       seed=seed)

    fill_edgedata_list(edgedata_list, G, nonedges_to_add, year_interval,
                       snapshots_dict, edges_exist=False)

    column_names = ['edge'] + \
                   ['ing_name', 'ed_name', 'ing_year', 'ed_year', 'age'] + \
                   ['age'] + \
                   snapshots_dict.values()[0].columns.values.tolist()

    df = pd.DataFrame(edgedata_list, columns=column_names)
    df.to_csv(experiment_data_dir + 'edge_data.csv')


def fill_edgedata_list(edgedata_list,
                       G,
                       edgelist_to_add,
                       year_interval,
                       snapshots_dict,
                       edges_exist):
    """
    Modifies edges_to_add_list in place by appending edge rows
    """

    # are we adding existing edges or non-existant edges
    if edges_exist:
        class_label = 1
    else:
        class_label = 0

    for edge in edgelist_to_add:

        # grab igraph vertices
        citing_vertex = G.vs(edge[0])
        cited_vertex = G.vs(edge[1])

        citing_year = citing_vertex['year'][0]

        # determine which vertex_df to retrieve
        ing_snapshot_year = citing_year + \
                            (year_interval - citing_year % year_interval)

        # get data from snapshot_dict
        ing_snapshot_df = snapshots_dict['vertex_metrics_' +
                                         str(ing_snapshot_year)]

        edgedata_list.append(edge_data_row(citing_vertex,
                                           cited_vertex, ing_snapshot_df))


def sample_non_edges(G, year_interval, num_non_edges_to_add, seed=None):
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
        np.random.seed(seed) # set seed for random packakge!

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
