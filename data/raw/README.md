# raw data

This folder contains the "raw data." [Raw data](http://simplystatistics.org/2016/07/20/relativity-raw-data/)
is relative, and our our case "raw" means downloaded from [Court Listener](https://www.courtlistener.com/)'s website.

This folder should only contain data if you plan on modifying/examining the cleaning pipeline. The purpose of this folder is A) make it easier for us to modify the pipeline in the future and B) make our science [reproducible](http://simplystatistics.org/2015/12/11/instead-of-research-on-reproducibility-just-do-reproducible-research/).

This folder may contain

case_metadata_master_r.csv
edgelist_master_r.csv
jurisdictions.csv

which are all raw versions of the similarly files located in clean/. This folder
is also where opinion and cluster files go when downloaded directly from Court Listener.  

**Do not delete this folder even if it is empty**
