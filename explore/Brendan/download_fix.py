__author__ = 'brendan'

import os
cwd = os.getcwd()
if '\explore\Brendan' in cwd:
    proj_dir = cwd[:-15]
data_dir = proj_dir + r'data/'
bren_curl_path='C:/Users/brendan/Downloads/curl-7.38.0-win64/bin/curl'

# DOWNLOAD DATA
# resource = 'clusters'
# download_data.download_bulk_resource('scotus', resource, data_dir)
# resource = 'opinions'
# download_data.download_bulk_resource('scotus', resource, data_dir)

# DOWNLOAD MASTER EDGE LIST
# download_data.download_master_edgelist(data_dir, use_curl=True, curl_path=bren_curl_path)

