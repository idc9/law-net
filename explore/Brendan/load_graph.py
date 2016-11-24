__author__ = 'brendan'

from code.pipeline import download_data
from code import load_data
import os
cwd = os.getcwd()
if '\explore\Brendan' in cwd:
    proj_dir = cwd[:-15]

data_dir = proj_dir + r'data/'

g = load_data.load_citation_network_igraph(data_dir, 'scotus', True)