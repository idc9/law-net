# law-net-iain


To create the node_metadata file for the entire network
```
from get_node_metadata import make_node_metadata_master
data_dir = 'data/'
make_node_metadata_master(data_dir, clean=True, remove=True)
```

To create the node_metadata for the FISC subnetwork

```
data_dir = 'data/'
court_name = 'fisc'
from download_data import make_node_metadata_court
make_node_metadata_court(court_name, data_dir, clean=True, remove=True)
```

To download the opinion and cluster cases from the Foreign Intelligence Surveillance Court

```
data_dir = 'data/'
from download_data import download_court_data
court_name, data_dir = 'fisc'
download_court_data(court_name, data_dir)
```
