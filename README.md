# law-net-iain

code/pipeline/ contains the data pipeline
download_data.py and make_raw_case_metadata.py

These grab the data from Court Listener and create csv files that contain the data we care about (e.g. case data, jurisdiction list, etc)

make_clean_data.py and cleaning_functions
These take the raw data and clean it i.e. get rid of the certiorari cases

To load the SCOTUS citation network (if cwd is explore/)

```
import networkx as nx
import pandas as pd

from load data import load_citation_network

data_dir = '../data/'

network = load_citation_network(data_dir, 'scotus')
```

To load the jurisdiction network
```
import networkx as nx
import pandas as pd

from load data import load_jurisdiction_network

data_dir = '../data/'

network = load_jurisdiction_network(data_dir)
```
