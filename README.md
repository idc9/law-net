# law-net-iain

To download the cases from the Foreign Intelligence Surveillance Court

```
data_dir = '../data/'
from download_data_batch import download_court_data
court_name, data_dir = 'fisc'
download_court_data(court_name, data_dir)
```