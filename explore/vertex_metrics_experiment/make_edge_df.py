from __future__ import division
import pandas as pd
import glob
import random as random


def get_snapshot_edge_metrics(G, experiment_data_dir, year_interval,
                              num_non_edges_to_add):
    """
    Creates the edge data frame. Rows are edges. Columns are the metrics
    of cited case in citing case's year (also year of citing case).

    Include all edges that exist in the network and
    randomly add non existent edges.

    Parameters
    ----------
    G: network

    path_to_vertex_metrics_folder: where can we find the vertex metrics

    year_interval: the year interval between each vertex metric .csv file

    num_non_edges_to_add: how many nonexistent edges to add

    Output
    --------
    Saves edge data frame as a csv file
    """
    # load all the vertex metric dataframes into a dict so
    # they only have to be read in once
    path_to_vertex_metrics_folder = experiment_data_dir + 'snapshots/'
    all_vertex_metrics_df = glob.glob(path_to_vertex_metrics_folder +
                                      "/vertex_metrics*.csv")
    vertex_metric_dict = {}
    for vertex_metrc_df in all_vertex_metrics_df:
        # add df to dict with filepath as key
        vertex_metric_dict[vertex_metrc_df] = pd.read_csv(vertex_metrc_df,
                                                          index_col=0)

    # list of edges that will be added to the edge df
    edges_to_add_list = []

    # get all present edges
    edges_to_add = G.get_edgelist()

    # go through each edge and add it to a list which will become the df
    for edge in edges_to_add:
        # get info from edge
        citing_year = G.vs(edge[0])['year'][0]
        cited_name = G.vs(edge[1])['name'][0]

        # determine which vertex_df to retrieve
        year = citing_year + (year_interval - citing_year % year_interval)

        # look-up that dataframe from given path
        vertex_df = vertex_metric_dict[path_to_vertex_metrics_folder +
                                       'vertex_metrics_' +
                                       str(year) + '.csv']

        # get row from df using cited_name
        row = vertex_df.loc[cited_name].values.tolist()

        edge_tuple = (1,) + tuple(row)
        edges_to_add_list.append(edge_tuple)

    # get a sample of non-present edges
    non_edges_to_add = sample_non_edges(G, year_interval, num_non_edges_to_add)

    # go through each sampled non-edge and
    # add it to the list already with edges
    for edge in non_edges_to_add:
        # get info from edge
        citing_year = G.vs(edge[0])['year'][0]
        cited_name = G.vs(edge[1])['name'][0]

        # determine which vertex_df to retrieve
        year = citing_year + (year_interval - citing_year % year_interval)

        # look-up that dataframe from given path
        vertex_df = vertex_metric_dict[path_to_vertex_metrics_folder +
                                       'vertex_metrics_' + str(year) + '.csv']

        # get row from df using cited_name
        row = vertex_df.loc[cited_name].values.tolist()

        edge_tuple = (0,) + tuple(row)
        edges_to_add_list.append(edge_tuple)

    # get column names from the last loaded dataframe
    # (since all df should have same column names)
    column_names = ['edge'] + list(vertex_df.columns.values)
    df = pd.DataFrame(edges_to_add_list, columns=column_names)

    # columns of df are the vertex of cited case in citing case's year

    df.to_csv(experiment_data_dir + 'edge_data.csv')


def sample_non_edges(G, year_interval, num_non_edges_to_add):
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
