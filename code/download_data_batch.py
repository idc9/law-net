import csv
import os
import requests
import ast
import tarfile
import time

username = 'unc_networks'
password = 'UNCSTATS'


def download_url(url, path=''):
    """
    This is a quick and easy function that simulates clicking a link in
    your browser that initiates a download.

    url:: the url from which data is to be downloaded.
    path:: the downloaded file to be created.
    """
    filename = path + url.split("/")[-1]

    with open(filename, "wb") as f:
        r = requests.get(url)
        f.write(r.content)


def download_court_data(court_name, data_dir):
    """
    Downloads the cluster and opinion files from a given court.

    If the cases are already all downloaded then skips the download. Otherwise
    this function downloads the .gzip file, unzips it then deletes the .gzip
    file.

    Parameters
    ----------
    court_name: string representing the court_name

    data_dir: path to the data directory

    e.g.
    from download_data_batch import download_court_data
    court_name, data_dir = 'fisc', '../data/'
    download_court_data(court_name, data_dir)
    """
    # TODO: create csv file containing all court names
    # check court_name is valid court name
    # with open('all_courts.csv', 'rb') as f:
    #     all_courts = list(csv(f))
    # if court_name not in all_courts:
    #     raise ValueError('invalid court_name')

    # Check that data_dir/raw/cases/ exists
    court_data_dir = data_dir + 'raw/' + court_name + '/cases/'
    cluster_data_dir = court_data_dir + 'clusters/'
    opinion_data_dir = court_data_dir + 'opinions/'

    if not os.path.exists(court_data_dir):
        os.makedirs(cluster_data_dir)
        os.makedirs(opinion_data_dir)

    start = time.time()
    download_bulk_resource(court_name, 'opinions', data_dir)
    end = time.time()
    print '%s opinions download took %d seconds' % (court_name, end - start)
    print

    start = time.time()
    download_bulk_resource(court_name, 'clusters', data_dir)
    end = time.time()
    print '%s clusters download took %d seconds' % (court_name, end - start)
    print


def download_bulk_resource(court_name, resource, data_dir):
    """
    Downloads the bulk data files for a given resouce from a given court

    Parameters
    ----------
    court_name: court to download files from

    resource: which resouce to download

    data_dir: relative path to data directory
    """
    if resource not in ['opinions', 'clusters']:
        raise ValueError('invalid resource')

    print 'requesting metadata for %s' % court_name
    court_metadata_url = 'https://www.courtlistener.com/api/rest/v3/%s/?docket__court=%s' % (resource, court_name)
    resource_data_dir = '%sraw/%s/cases/%s/' % (data_dir, court_name, resource)

    # check if we already have all cases
    court_metadata = url_to_dict(court_metadata_url)
    num_files_on_server = court_metadata['count']

    files_in_dir = os.listdir(resource_data_dir)
    num_files_in_dir = len(files_in_dir)

    # If the number of files downloaded isn't the
    # same as the number on the server
    if num_files_on_server != num_files_in_dir:
        print 'Downloading %s data for court %s...' % \
                (resource, court_name.upper())

        # Delete the files we currently have
        print '...deleting files...'
        for filename in files_in_dir:
            os.remove(r'%s/%s' % (resource_data_dir, filename))

        # Download the .tar.gz file
        print '...downloading new .tar.gz file...'
        resource_url = 'https://www.courtlistener.com/api/bulk-data/%s/%s.tar.gz' % (resource, court_name)
        download_url(url=resource_url,
                     path=resource_data_dir)

        # Extract it
        print '...extracting files...'
        with tarfile.open(resource_data_dir + '%s.tar.gz' % court_name) as tf:
            tf.extractall(path=resource_data_dir)
        # And delete .tar.gz file
        os.remove('%s/%s.tar.gz' % (resource_data_dir, court_name))

        print '...done.'

    else:
        print "All %s %s files accounted for." % (court_name, resource)


def url_to_dict(url):
    """
    :param url: String representing a json-style object on Court Listener's
    REST API

    :return: html_as_dict, a dictionary of the data on the HTML page
    """
    response = requests.get(url, auth=(username, password))
    html = response.text
    html = html.replace('false', 'False')
    html = html.replace('true', 'True')
    html = html.replace('null', 'None')
    html_as_dict = ast.literal_eval(html)
    return html_as_dict
