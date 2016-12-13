from __future__ import division
import pandas as pd
import random as random
import copy
import os

from pipeline_helper_functions import *
from similarity_matrix import *
from get_edge_data import *


def make_edge_df(G, experiment_data_dir, active_years,
                 num_non_edges_to_add, columns_to_use, seed=None):
    """
    Creates the edge data frame

    Parameters
    ----------
    G:

    experiment_data_dir:

    active_years:

    num_non_edges_to_add:

    columns_to_use:

    seed:
    """
    # load snapshot dataframes
    snapshots_dict = load_snapshots(experiment_data_dir)

    if len(snapshots_dict) == 0:
        raise ValueError('failed ot load snapshots train')

    # mabye load the similarities
    if 'similarity' in columns_to_use:
        similarity_matrix, CLid_to_index = load_similarity_matrix(experiment_data_dir)
    else:
        similarity_matrix = None
        CLid_to_index = None

    # initialize edge data frame
    colnames = copy.deepcopy(columns_to_use)
    colnames.append('is_edge')
    edge_data = pd.DataFrame(columns=colnames)

    # get all present edges
    present_edgelist = get_present_edges(G, active_years)

    # organize edges by ing snapshot year
    edges_by_snap_year_dict = get_edges_by_snapshot_dict(G, present_edgelist,
                                                         active_years)

    # add present edge data
    for year in active_years:
        snapshot_year = year - 1

        # vertex metrcs in snapshot year
        snapshot_df = snapshots_dict['vertex_metrics_' + str(snapshot_year)]

        # edges to add whose ing year is in the snapshot year
        edges = edges_by_snap_year_dict[snapshot_year]

        # get snapshot year edge data frame
        sn_edge_data = get_edge_data(G, edges, snapshot_df, columns_to_use,
                                     similarity_matrix, CLid_to_index,
                                     edge_status='present')

        edge_data = edge_data.append(sn_edge_data)

    # get a sample of non-present edges
    absent_edgelist = sample_absent_edges(G, num_non_edges_to_add,
                                          active_years, seed=seed)

    # organize edges by ing snapshot year
    edges_by_snap_year_dict = get_edges_by_snapshot_dict(G, absent_edgelist,
                                                         active_years)

    # add absent edge data
    for year in active_years:
        snapshot_year = year - 1

        # vertex metrcs in snapshot year
        snapshot_df = snapshots_dict['vertex_metrics_' + str(snapshot_year)]

        # edges to add whos ing year is in the snapshot year
        edges = edges_by_snap_year_dict[snapshot_year]

        # get edge data frame for snapshot year
        sn_edge_data = get_edge_data(G, edges, snapshot_df, columns_to_use,
                                     similarity_matrix, CLid_to_index,
                                     edge_status='absent')

        edge_data = edge_data.append(sn_edge_data)

    edge_data.to_csv(experiment_data_dir + 'edge_data.csv')


def update_edge_df(G, experiment_data_dir, active_years, columns_to_add):
    """
    Adds new columns to edge_data frame
    """
    # load snapshot dataframes
    snapshots_dict = load_snapshots(experiment_data_dir)

    if len(snapshots_dict) == 0:
        raise ValueError('failed ot load snapshots train')

    # load edge data frame
    edge_data_path = experiment_data_dir + 'edge_data.csv'
    if os.path.exists(edge_data_path):
        edge_data = pd.read_csv(edge_data_path, index_col=0)
    else:
        raise ValueError('cant find edge data')

    # mabye load the similarities
    if 'similarity' in columns_to_add:
        similarity_matrix, CLid_to_index = load_similarity_matrix(experiment_data_dir)
    else:
        similarity_matrix = None
        CLid_to_index = None

    # get edges that are in edge_data then convert them to igraph indices
    edgelist_CLid = [get_edges_from_str(e) for e in edge_data.index]
    edgelist = [CLid_edge_to_IGid(G, e) for e in edgelist_CLid]

    # organize edges by ing snapshot year
    edges_by_snap_year_dict = get_edges_by_snapshot_dict(G, edgelist,
                                                         active_years)

    # initialize temp dataframe
    edge_data_to_add = pd.DataFrame(columns=columns_to_add)

    # add present edge data
    for sn_year in active_years:
        # vertex metrcs in snapshot year
        snapshot_df = snapshots_dict['vertex_metrics_' + str(sn_year)]

        # edges to add whose ing year is in the snapshot year
        edges = edges_by_snap_year_dict[sn_year]

        # get snapshot year edge data frame
        sn_edge_data = get_edge_data(G, edges, snapshot_df, columns_to_add,
                                     similarity_matrix, CLid_to_index)
        edge_data_to_add = edge_data_to_add.append(sn_edge_data)

    # add new columns
    edge_data[colums_to_add] = edge_data_to_add

    # save updated edge dataframe
    edge_data.to_csv(edge_data_path)


def get_edges_from_str(s):
    """
    Helper function for update_edge_df(). Converts string representation of
    an edge to a tuple
    """
    split = s.split('_')
    return split[0], split[1]


def CLid_edge_to_IGid(G, edge):
    """
    Returns the igraph indices for an edge from their CL ids
    """
    return G.vs.find(name_eq=edge[0]).index, G.vs.find(name_eq=edge[1]).index


def get_edges_by_snapshot_dict(G, edgelist, active_years):
    """
    Organizes edges by ing snapshot year (year before citing year)

    list is igraph indices
    """
    num_edges = len(edgelist)

    # get the citing year of each edge
    snap_years = [G.vs[edge[0]]['year'] - 1 for edge in edgelist]

    # dict that organizes edges by ing snapshot year
    edges_by_ing_snap_year_dict = {y-1: [] for y in active_years}
    for i in range(num_edges):
        edges_by_ing_snap_year_dict[snap_years[i]].append(edgelist[i])

    return edges_by_ing_snap_year_dict


def sample_absent_edges(G, num_samples, active_years, seed=None):
    '''
    Samples a number of nonexistent edges from the network G

    - citing year must be within active year range
    - cited year must be less than citing year - 1

    Parameters
    ----------
    G: network

    num_samples: number of desired samplese

    active_years: the allowed years for ing cases

    seed: sampling seed

    Output
    --------
    List of absent edges (igraph indices)
    '''
    if seed:
        random.seed(seed)

    # samples to return
    samples = set()

    # edges currently in graph
    present_edges = set(G.get_edgelist())

    # vertices to sample from
    vertices = set(G.vs.select(year_le=max(active_years)))

    # ing_year should be in (min, max) of active_years
    min_ing_year = min(active_years)

    # run until we get enough samples
    while len(samples) < num_samples:
        # sample a pair of vertices
        pair = random.sample(vertices, 2)  # default: without replacement

        year0 = G.vs(pair[0].index)['year'][0]
        year1 = G.vs(pair[1].index)['year'][0]

        # if years are the same or neither of the years are
        # above the min active year
        if (year0 != year1) and (min_ing_year < year0 or min_ing_year < year1):

            # the larger year is the citing year
            if year0 < year1:
                random_edge = (pair[1].index, pair[0].index)
            else:
                random_edge = (pair[0].index, pair[1].index)

            # make sure edge is absent and that we haven't already added it
            if random_edge not in present_edges and random_edge not in samples:
                samples.add(random_edge)

    return list(samples)


def get_present_edges(G, active_years):
    """
    Returns all edges in graph satisfying
    - citing year withing ing_years range
    - cited year < citing year

    Parameters
    ---------
    G: igraph object

    active_years: range of allowable citing years

    Output
    -------
    list of edge tuples (igraph indices)
    """
    min_year = min(active_years)
    max_year = max(active_years)

    return [(e.source, e.target) for e in G.es
            if (min_year <= G.vs[e.source]['year'] <= max_year) and
               (G.vs[e.target]['year'] < G.vs[e.source]['year'])]
