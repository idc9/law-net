import os
import pandas as pd

from pipeline.download_data import download_bulk_resource
from pipeline.make_raw_case_metadata import get_raw_case_metadata_from_court
from make_case_text_files import make_text_files


def download_op_and_cl_files(data_dir, network_name):
    """
    Downloads the opinion and cluster files from courtlistener for each
    jurisdiction
    """

    # which courts to add download from
    courts = get_courts(network_name)

    for court in courts:
        download_bulk_resource(court, 'clusters', data_dir)
        download_bulk_resource(court, 'opinions', data_dir)


def make_subnetwork_raw_case_metadata(data_dir, network_name):
    """
    Create the raw case meta data data frame for the network

    Parameters
    ----------
    data_dir:

    network_name: either 'scotus' or 'federal'
    """
    # directories
    raw_dir = data_dir + 'raw/'
    raw_md_path = raw_dir + network_name + '_case_metadata_r.csv'

    # which courts to add to network
    courts = get_courts(network_name)

    # get metadata from each jurisdiction
    for court in courts:
        court_data = get_raw_case_metadata_from_court(court, data_dir)

        # either initialize of append data frame
        if court == courts[0]:
            r_case_metadata = court_data
        else:
            r_case_metadata = case_metadata.append(court_data)

    # save raw case metadata data frame
    r_case_metadata.to_csv(raw_md_path, index=True)


def clean_metadata_and_edgelist(data_dir, network_name):
    """
    Builds the clean metadata data frame and edgelist for the given network

    - remove SCOTUS cases missing scdb ids
    - remove detroit lumber case
    - gets egelist of subnetwork
    """

    # directory paths
    raw_dir = data_dir + 'raw/'
    subnet_dir = data_dir + network_name + '/'

    # file locations
    raw_md_path = raw_dir + network_name + '_case_metadata_r.csv'
    clean_md_path = subnet_dir + 'case_metadata.csv'
    master_el_path = raw_dir + 'edgelist_master_r.csv'
    clean_el_path = subnet_dir + 'edgelist.csv'

    # load raw metadata and master edgelist
    case_metadata = pd.read_csv(raw_md_path, index_col=0)
    case_metadata.index = case_metadata.index.astype('str')
    master_edgelist = pd.read_csv(master_el_path)

    # scotus scdb ids
    scotus_scdb_ids = case_metadata[case_metadata['court'] == 'scotus']['scdb_id']

    # scotus cases with no scdb id
    no_scdb_link = scotus_scdb_ids.index[scotus_scdb_ids.isnull()].tolist()

    # remove SCOTUS cases with no SCDB id
    case_metadata.drop(no_scdb_link, inplace=True)

    # kill detroit lumber
    if '96405' in set(case_metadata.index):
        case_metadata.drop('96405', inplace=True)

    # only keep edges for whom both vertices are in case metadata data frame
    op_ids = set(case_metadata.index)
    edgelist = master_edgelist[master_edgelist.citing.isin(op_ids) &
                               master_edgelist.cited.isin(op_ids)]

    # save the clean edgelist edgelist and case metadata
    edgelist.to_csv(clean_el_path, index=False)
    case_metadata.to_csv(clean_md_path, index=True)


def make_network_textfiles(data_dir, network_name):

    # directories
    subnet_dir = data_dir + '%s/' % network_name
    text_dir = subnet_dir + 'textfiles/'
    clean_md_path = subnet_dir + 'case_metadata.csv'

    # get op_ids to use from clean case metadata
    case_metadata = pd.read_csv(clean_md_path, index_col=0)
    case_metadata.index = case_metadata.index.astype('str')
    op_ids_good = case_metadata.index

    # which courts to get textfiles for
    courts = get_courts(network_name)

    # get textfiles for each court
    for court in courts:

        make_text_files(data_dir,
                        court,
                        network_name,
                        op_id_good=op_ids_good,
                        op_id_bad=None)


def get_courts(network_name):
    """
    Returns the list of courts that are in a given network

    Currently supports the federal court network and individual jurisdictions
    """
    # which courts to add to the network
    if network_name == 'federal':
        courts = ['scotus', 'cafc', 'cadc']
        courts += ['ca' + str(i+1) for i in range(11)]
    else:
        courts = [network_name]

    return courts
