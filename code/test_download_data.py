import os

from nose.tools import assert_equal, assert_true

from download_data import *

data_dir = '../data/'


def test_download_url():
    court_name = 'fisc'
    url = 'https://www.courtlistener.com/api/bulk-data/clusters/%s.tar.gz' % \
          court_name

    download_url(url)
    download_success = court_name + '.tar.gz' in os.listdir(os.getcwd())

    if download_success:
        os.remove(court_name + '.tar.gz')

    assert_true(download_success)


def test_download_court_data():
    court_name = 'fisc'  # only a few cases

    download_court_data(court_name, data_dir)
    opinion_dir = data_dir + 'raw/%s/cases/opinions/' % court_name
    assert_true('2360191.json' in os.listdir(opinion_dir))

    # make sure this still works when cases are already there
    download_court_data(court_name, data_dir)
    assert_true('2360191.json' in os.listdir(opinion_dir))
