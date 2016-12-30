import os
import requests


def setup_data_dir(data_dir):
    """
    Initializes the data directory

    data_dir
        raw
        scdb

    raw holds data downloaded from CourtListener i.e. opinion/cluster files
    master edgelist etc

    scdb holds data from supreme court data base

    """

    if not os.path.exists(data_dir):
        # make the top directory
        os.mkdir(data_dir)

        # holds the raw data i.e. opinion/cluster files, master edgelist
        os.mkdir(data_dir + 'raw')

        # holds data from scdb
        os.mkdir(data_dir + 'scdb')


def make_subnetwork_directory(data_dir, network_name):
    """
    Set up subnetwork data directory

    data_dir
        raw
        scdb
        subnet_dir
            textfiles
            nlp
            snapshots

    Parameters
    ----------
    data_dir: path to overall data directory

    network_name: name of subnetwork
    """
    subnet_dir = data_dir + network_name + '/'

    if not os.path.exists(subnet_dir):
        os.makedirs(subnet_dir)

        # opinion text files go here
        os.makedirs(subnet_dir + 'textfiles/')

        # cached NLP data goes here
        os.makedirs(subnet_dir + 'nlp/')

        # for vertex metrics experiment
        os.makedirs(subnet_dir + 'snapshots/')
