import os

import pandas as pd

from cleaning_functions import *
from make_raw_case_metadata import make_raw_case_metadata_master
from download_data import download_master_edgelist


def make_clean_case_metadata(data_dir, overwrite=False):
    """
    Applies the cleaning functions to the raw case_metadata_master.csv file in
    the raw/ folder. If the raw metadata file does not exist then download it.

    Parameters
    ---------

    data_dir: path to data directory

    overwrite: if the file already exists in the clean folder overwrite it
    """
    # TODO: implement some cleaning functions
    # if the master file is already there don't overwrite it unless told to
    if os.path.isfile(data_dir + 'clean/case_metadata_master.csv'):
        if overwrite:
            os.remove(data_dir + 'clean/case_metadata_master.csv')
        else:
            raise ValueError('case metadata file already exists')

    # if case_metadata_master_r does not exist then download it
    if not os.path.isfile(data_dir + 'raw/case_metadata_master_r.csv'):
        make_raw_case_metadata_master(data_dir, remove=True)

    raw_metadata = pd.read_csv(data_dir + 'raw/case_metadata_master_r.csv',
                               index_col='id')

    # TODO: create additional cleaning functions
    cert_cases = get_cert_cases_scotus(data_dir)
    # pd.DataFrame({'cert': cert_cases}).to_csv(data_dir + 'raw/cert.csv')

    clean_metadata = raw_metadata.drop(cert_cases)

    clean_metadata.to_csv(data_dir + 'clean/case_metadata_master.csv',
                          index=True)


def make_clean_edgelist(data_dir, overwrite=False):
    """
    Applies the cleaning functions to the raw case_metadata_master.csv file in
    the raw/ folder. If the raw metadata file does not exist then download it.

    Parameters
    ---------

    data_dir: path to data directory

    overwrite: if the file already exists in the clean folder overwrite it
    """
    # TODO: implement some cleaning functions
    # if the master file is already there don't overwrite it unless told to
    if (not overwrite) and (os.path.isfile(data_dir + 'clean/case_metadata_master.csv')):
        raise ValueError('case metadata file already exists')

    # if case_metadata_master_r does not exist then download it
    if not os.path.isfile(data_dir + 'raw/edgelist_master_r.csv'):
        download_master_edgelist(data_dir)

    # TODO: create additional cleaning functions

    clean_edgelist = find_time_travelers(data_dir)

    clean_edgelist.to_csv(data_dir + 'clean/edgelist_master.csv', index=False)


def make_clean_jurisdiction_file(data_dir):
    """
    Applies the cleaning functions to the raw jurisdictions.csv file in
    the raw/ folder. If the raw jurisdictions file does
    not exist then download it.
    """
    # raw_jurisdiction_df = pd.read_csv(data_dir + 'raw/jurisdictions.csv')
    clean_jurisdiction_df = get_clean_jurisdiction(data_dir)
    clean_jurisdiction_df.to_csv(data_dir + 'clean/jurisdictions.csv',
                                 index=False)


def make_jurisdiction_edgelist(data_dir):
    """
    Creates the weighted jurisdiction adjacency matrix where the weights
    are the number of citations from one court to another.

    Output
    ------
    saves a csv file version of the adjacency matrix
    """

    edgelist = pd.read_csv(data_dir + 'clean/edgelist_master.csv')
    case_metadata = pd.read_csv(data_dir + 'clean/case_metadata_master.csv',
                                index_col='id')
    jurisdictions = pd.read_csv(data_dir + 'clean/jurisdictions.csv',
                                index_col='court')

    court_adj = pd.DataFrame(0,
                             index=jurisdictions.index.tolist(),
                             columns=jurisdictions.index.tolist())

    id_to_court = case_metadata.court.to_dict()
    for index, edge in edgelist.iterrows():
        if not edge['case_mia']:
            ing_court = id_to_court[edge['citing']]
            ed_court = id_to_court[edge['cited']]

            court_adj.loc[ing_court, ed_court] += 1

    court_adj.to_csv(data_dir + 'clean/jurisdictions_adj_mat.csv')


def make_court_subnetwork(court_name, data_dir):
    """
    Creates the case_metadata and edgelist files for the given court.
    Will use the case_metadata_master and edgelist master files by default if
    they exist in the clean directory.

    If they do not exist then will create the case_metadata and edgelist
    manuelly from the clusters/ and opinions/ files in the raw data folder and
    apply the cleaning functions directly to them.

    If these files are not on the local computer they will be downloaded.
    """

    if not os.path.isfile(data_dir + 'clean/case_metadata_master.csv'):
        raise ValueError('case_metadata_master.csv does not exist')

    if not os.path.isfile(data_dir + 'clean/edgelist_master.csv'):
        raise ValueError('edgelist_master.csv does not exist')

    edgelist = pd.read_csv(data_dir + 'clean/edgelist_master.csv')
    metadata = pd.read_csv(data_dir + 'clean/case_metadata_master.csv',
                           index_col='id')

    # subset out cases from the given court
    metadata_court = metadata[metadata.court == court_name]

    # graph the cases id which are in the given court
    case_ids = set(metadata_court.index)
    edgelist_court = edgelist[edgelist.citing.isin(case_ids) & edgelist.cited.isin(case_ids)]

    # if the files already exist then kill them
    court_dir = data_dir + 'clean/%s/' % court_name
    EL_path = court_dir + 'edgelist.csv'
    CMD_path = court_dir + 'case_metadata.csv'

    if not os.path.exists(court_dir):
        os.makedirs(court_dir)
    else:
        if os.path.exists(EL_path):
            os.remove(EL_path)
        if os.path.exists(CMD_path):
            os.remove(CMD_path)

    edgelist_court.to_csv(EL_path)
    metadata_court.to_csv(CMD_path)
