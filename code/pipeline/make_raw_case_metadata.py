import os
import json
import datetime
import time
import shutil
import re

import pandas as pd
import numpy as np

from download_data import download_bulk_resource


def make_raw_case_metadata_master(data_dir, remove=True):
    """
    Creates the node_metadata.csv file all jurisdictions. Note that if the
    node_metadata.csv file already exists it will be overwritten.

    Parameters
    --------
    court_name: which court

    data_dir: path to data directory

    remove: if true will remove .json files

    Output
    ------
    Saves a csv file containing case metadata
    """
    jurisdictions = pd.read_csv(data_dir + 'raw/jurisdictions.csv')

    file_path = data_dir + 'raw/case_metadata_master_r.csv'

    # if the node_metadata file already exsists kill it
    if os.path.isfile(file_path):
        os.remove(file_path)

    all_courts = jurisdictions['Abbrev'].tolist()
    # nc_courts = []
    # for court in jurisdictions.index:
    #     if jurisdictions.loc[court, 'horizontal'] == 'NC':
    #         nc_courts.append(court)

    start = time.time()

    # start with scotus scotus
    metadata = get_raw_case_metadata_from_court(all_courts[0],
                                                data_dir,
                                                remove=remove)
    # append all other courts
    for court in all_courts[1:]:
        court_data = get_raw_case_metadata_from_court(court,
                                                      data_dir,
                                                      remove=remove)
        metadata = metadata.append(court_data)
    end = time.time()

    print 'creating the entire network node metadata file took %d seconds' \
          % (end - start)

    metadata.to_csv(file_path)

    # kill the rest of the empty jurisdiction folders
    if remove:
        for court in all_courts:
            court_dir = data_dir + 'raw/%s/' % court
            if len(os.listdir(court_dir)) == 0:
                os.rmdir(court_dir)


def make_raw_case_metadata_court(court_name, data_dir):
    """
    Creates the node_metadata.csv file for a given court. Note that if the
    node_metadata.csv file already exists it will be overwritten.

    Parameters
    --------
    court_name: which court

    data_dir: path to data directory

    remove: if true will remove .json files
    """

    metadata = get_raw_case_metadata_from_court(court_name, data_dir, remove)

    court_path = data_dir + 'raw/%s/' % court_name
    md_path = court_path + 'case_metadata_r.csv'

    # check if court folder exists
    if os.path.exists(court_path):

        # if the medtadata is already there kill it
        if os.path.isfile(md_path):
            os.remove(md_path)
    else:
        # make court folder if it doesn't exist
        os.makedirs(court_path)

    metadata.to_csv(md_path)


def get_raw_case_metadata_from_court(court_name, data_dir):
    """
    Returns a pandas DatFrame that has the case metadata for each case in
    the given court. Will download json files if they are not already on
    local computer.

    Currently only gets meatadata from cluster files
    Parameters
    ----------
    court_name: court

    data_dir: path to data directory

    remove: if True will remove all case files

    Output
    ------
    Returns a pandas DataFrame
    """
    cluster_dir = data_dir + 'raw/%s/clusters/' % court_name
    opinion_dir = data_dir + 'raw/%s/opinions/' % court_name

    clusters_already_exist = os.path.exists(cluster_dir)
    opinions_already_exist = os.path.exists(opinion_dir)

    # download cases if they are not already on local computer
    if not clusters_already_exist:
        os.makedirs(cluster_dir)
        download_bulk_resource(court_name, 'clusters', data_dir)

    # download cases if they are not already on local computer
    if not opinions_already_exist:
        os.makedirs(opinion_dir)
        download_bulk_resource(court_name, 'opinions', data_dir)

    # all cluster and opinion files
    cluster_files = os.listdir(cluster_dir)
    opinion_files = os.listdir(opinion_dir)

    # dicitonary mapping opinion ids to cluster ids
    op_to_cl = get_opinion_to_cluster_dict(data_dir, court_name)

    # initialize data frame
    df_cols = ['date', 'court', 'name', 'judges', 'scdb_id', 'term']
    metadata = pd.DataFrame(index=op_to_cl.keys(),
                            columns=df_cols)
    metadata.index.name = 'id'

    # get metadata for each opinion
    for op_id in op_to_cl.keys():

        # get cluster id
        cl_id = op_to_cl[op_id]

        # metadata from cluster file
        cl_data = get_cluster_data(path=cluster_dir + cl_id + '.json')

        # add row to data frame
        metadata.loc[op_id, 'date'] = cl_data['date']
        metadata.loc[op_id, 'court'] = court_name
        metadata.loc[op_id, 'name'] = cl_data['name']
        metadata.loc[op_id, 'judges'] = cl_data['judges']
        metadata.loc[op_id, 'scdb_id'] = cl_data['scdb_id']
        metadata.loc[op_id, 'term'] = cl_data['term']

    # which columns to include from SCDB
    scdb_cols = ['issueArea', 'decisionDirection', 'majVotes', 'minVotes']
    if court_name == 'scotus':

        # load scdb data frames
        scdb_modern = pd.read_csv(data_dir + 'scdb/SCDB_2016_01_caseCentered_Citation.csv', index_col=0)
        scdb_legacy = pd.read_csv(data_dir + 'scdb/SCDB_Legacy_03_caseCentered_Citation.csv', index_col=0)
        scdb = scdb_legacy.append(scdb_modern)

        # addd in the desired columns
        metadata = metadata.merge(scdb[scdb_cols],
                                  how="left",
                                  left_on="scdb_id",
                                  right_index=True)
    else:
        for c in scdb_cols:
            metadata[c] = np.nan

    return metadata


def get_cluster_data(path):
    """
    Gets data from a cluster.json file

    Parameters
    ---------

    path: path to .json file
    """
    cl_dict = json_to_dict(path)
    data = {}

    # add the case date
    year, month, day = [int(e) for e in cl_dict['date_filed'].rsplit('-')]
    data['date'] = datetime.date(year=year, month=month, day=day)

    # add the term
    # TODO: ass court name
    data['term'] = get_term(data['date']) #,court_name

    data['name'] = cl_dict['slug'].encode('ascii', 'ignore')

    data['judges'] = cl_dict['judges'].encode('ascii', 'ignore')

    data['scdb_id'] = cl_dict['scdb_id']



    return data


def get_opinion_data(path):
    """
    Gets data from an opinion.json file

    Parameters
    ---------

    path: path to .json file
    """
    op_dict = json_to_dict(path)
    data = {}

    year, month, day = [int(e) for e in op_dict['date_modified'].
                        rsplit('T')[0].rsplit('-')]
    data['op_modified'] = datetime.date(year=year, month=month, day=day)

    return data


def json_to_dict(path):
    """
    Given a path to a .json file returns a dict of the .json file

    Parameters
    ----------

    path: path to .json file

    Output:
    dict of json file
    """
    with open(path) as data_file:
        data = json.load(data_file)
        return data


def remove_folder(path):
    """
    Kills a directory that is not empty
    """
    if len(path) <= 2:
        raise ValueError('DANGER ZONE MAKE SURE THIS IS WHAT YOU WANT')

    # check if folder exists
    if os.path.exists(path):
        # remove if exists
        shutil.rmtree(path)


def update_court_metadata_raw(data_dir, court_name):
    """
    Updates the master raw case metadata for a jurisdiction
    """

    md_path = data_dir + 'raw/case_metadata_master_r.csv'

    # load old metadata file
    case_md = pd.read_csv(md_path, index_col='id')

    # remove old cases
    case_md = case_md[case_md.court != court_name]

    # get updated case metadata
    updated_court_md = get_raw_case_metadata_from_court(court_name, data_dir,
                                                        remove=True)

    # update case metadata file
    case_md = case_md.append(updated_court_md)

    case_md.to_csv(md_path, index=True)


def get_term(date, court_name='scotus'):
    """
    Returns the term of a case
    e.g. 2015-2016 term would be labeled 2015

    Parameters
    ----------
    date: the date of the case (datetime date)

    court_name: which jurisdiction
    """
    if court_name == 'scotus':
        cutoff_month = 9

    if date.month <= cutoff_month:
        term = date.year - 1
    else:
        term = date.year

    return term


def get_opinion_to_cluster_dict(data_dir, court_name):
    """
    Returns a dictionary mapping opinion id to cluster id

    Many opinions to one cluster
    """

    # directory containing clusters
    cluster_dir = data_dir + 'raw/%s/clusters/' % court_name

    # cluster ids of all cluster files
    cl_ids = [c.split('.json')[0] for c in os.listdir(cluster_dir)]

    # dictionary mapping clusters to list of opinions contained in the cluster
    op_to_cl = {}

    # go through each cluster file
    for cl_id in cl_ids:

        # dict of cluster json file
        cl_dict = json_to_dict(cluster_dir + cl_id + '.json')

        # get the list of opinion ids from each cluster file
        op_ids = [re.search(".+opinions\/(\d+?)\/", s).group(1)
                  for s in cl_dict['sub_opinions']]

        # create entry in dict for each opinion (op id -> cl id)
        for op_id in op_ids:
            op_to_cl[str(op_id)] = cl_id

    return op_to_cl
