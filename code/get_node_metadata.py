import os
import json
import datetime
import time

import pandas as pd

from download_data import download_bulk_resource
from clean_jurisdiction import load_jurisdictions


def make_node_metadata_master(data_dir, clean=False, remove=True):
    """
    Creates the node_metadata.csv file all jurisdictions. Note that if the
    node_metadata.csv file already exists it will be overwritten.

    Parameters
    --------
    court_name: which court

    data_dir: path to data directory

    clean: if True will place file in data/clean/court_name/network folder
    otherwise will place file in data/raw/court_name/network folder

    remove: if true will remove .json files

    Output
    ------
    Saves a csv file containing node metadata
    """
    jurisdictions = load_jurisdictions(data_dir)

    if clean:
        file_path = data_dir + 'clean/node_metadata_master.csv'
    else:
        file_path = data_dir + 'raw/node_metadata_master_r.csv'

    # if the node_metadata file already exsists kill it
    if os.path.isfile(file_path):
        os.remove(file_path)

    all_courts = jurisdictions.index.tolist()
    # nc_courts = []
    # for court in jurisdictions.index:
    #     if jurisdictions.loc[court, 'horizontal'] == 'NC':
    #         nc_courts.append(court)

    metadata = get_case_metadata_from_court(all_courts[0],
                                            data_dir, remove=remove)

    start = time.time()
    for court in all_courts[1:]:
        court_data = get_case_metadata_from_court(court,
                                                  data_dir,
                                                  remove=remove)
        metadata = metadata.append(court_data)
    end = time.time()

    print 'creating the entire network node metadata file took %d seconds' \
          % (end - start)

    metadata.to_csv(file_path)

    # kill the rest of the empty jurisdiction folders
    if remove:
        for court in nc_courts:
            court_dir = data_dir + 'raw/%s/' % court
            if len(os.listdir(court_dir)) == 0:
                os.rmdir(court_dir)


def make_node_metadata_court(court_name, data_dir,
                             clean=False, remove=True):
    """
    Creates the node_metadata.csv file for a given court. Note that if the
    node_metadata.csv file already exists it will be overwritten.

    Parameters
    --------
    court_name: which court

    data_dir: path to data directory

    clean: if True will place file in data/clean/court_name/network folder
    otherwise will place file in data/raw/court_name/network folder

    remove: if true will remove .json files
    """

    metadata = get_case_metadata_from_court(court_name, data_dir, remove)

    if clean:
        network_path = data_dir + 'clean/' + court_name + '/network/'
        file_name = 'node_metadata.csv'
    else:
        network_path = data_dir + 'raw/' + court_name + '/network/'
        file_name = 'node_metadata_r.csv'

    if not os.path.exists(network_path):
        os.makedirs(network_path)
    else:
        if os.path.isfile(network_path + file_name):
            os.remove(network_path + file_name)

    metadata.to_csv(network_path + file_name)


def get_case_metadata_from_court(court_name, data_dir, remove=True):
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

    cluster_dir = data_dir + 'raw/%s/cases/clusters/' % court_name
    # opinion_dir = data_dir + 'raw/%s/cases/opinions/' % court_name

    # download cases if they are not already on local computer
    if not os.path.exists(cluster_dir):
        os.makedirs(cluster_dir)

        # grab cluster files
        start = time.time()
        download_bulk_resource(court_name, 'clusters', data_dir)
        end = time.time()
        print '%s clusters download took %d seconds' % \
              (court_name, end - start)
        print

    # all cluster and opinion files
    clusters = os.listdir(cluster_dir)
    # opinions = os.listdir(opinion_dir)

    # opinion_no_cluster = set(opinions).difference(set(clusters))
    # cluster_no_opinion = set(clusters).difference(set(opinions))
    # all_cases = [c.split('.')[0] for c in set(opinions).union(set(clusters))]
    all_cases = [c.split('.')[0] for c in clusters]
    # print '%s cluster files, %s opinion %s files detected.' % \
    #       (len(clusters), len(opinions), court_name)

    # if set(clusters) != set(opinions):
    #     print 'WARNING %s cluster and opinion files not equal' % court_name
    #     print '%d cases with opinion but no cluster' %len(opinion_no_cluster)
    #     print '%d cases with cluster but no opinion' %len(cluster_no_opinion)
    #     print '%d cases in total' % len(all_cases)
    #     print

    # cols = ['date', 'court', 'name', 'judges', 'has_opinion', 'has_cluster',
    #         'cl_modified', 'op_modified']

    cols = ['date', 'court', 'name', 'judges', 'cl_modified']
    metadata = pd.DataFrame(index=all_cases, columns=cols)
    metadata.index.name = 'id'
    # metadata.has_cluster.fillna(value=False, inplace=True)
    # metadata.has_opinion.fillna(value=False, inplace=True)

    print 'scraping clusters....'
    start = time.time()
    for cl_file in clusters:
        case_id = cl_file.split('.')[0]

        cl_data = get_cluster_data(path=cluster_dir + cl_file)

        metadata.loc[case_id, 'date'] = cl_data['date']
        metadata.loc[case_id, 'court'] = court_name
        metadata.loc[case_id, 'name'] = cl_data['name']
        metadata.loc[case_id, 'judges'] = cl_data['judges']
        # metadata.loc[case_id, 'has_cluster'] = True
        metadata.loc[case_id, 'cl_modified'] = cl_data['cl_modified']
    end = time.time()

    print 'scraping the %s clusters took %d seconds' % (court_name, end-start)
    print

    # print 'scraping opinions....'
    # start = time.time()
    # for op_file in opinions:
    #     case_id = op_file.split('.')[0]
    #
    #     op_data = get_opinion_data(path=opinion_dir + op_file)
    #
    #     metadata.loc[case_id, 'has_opinion'] = True
    #     metadata.loc[case_id, 'op_modified'] = op_data['op_modified']
    #
    # end = time.time()
    # print 'scraping the %s opinions took %d seconds' % \
    #        (court_name, end-start)
    # print

    if remove:
        for case in os.listdir(cluster_dir):
            os.remove(cluster_dir + case)

        # for case in os.listdir(opinion_dir):
        #     os.remove(opinion_dir + case)

        os.rmdir(cluster_dir)
        # os.rmdir(opinion_dir)
        os.rmdir(data_dir + 'raw/%s/cases/' % court_name)

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

    year, month, day = [int(e) for e in cl_dict['date_filed'].rsplit('-')]
    data['date'] = datetime.date(year=year, month=month, day=day)

    data['name'] = cl_dict['slug'].encode('ascii', 'ignore')

    data['judges'] = cl_dict['judges'].encode('ascii', 'ignore')

    year, month, day = [int(e) for e in cl_dict['date_modified'].
                        rsplit('T')[0].rsplit('-')]
    data['cl_modified'] = datetime.date(year=year, month=month, day=day)

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
