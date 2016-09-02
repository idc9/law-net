# clean data

This folder contains the "clean" data you use in your analysis. It should
include the following files:

case_metadata_master.csv
edgelist_master.csv
jurisdictions.csv
jurisdiction_adj_mat.csv

Optionally may include saved subnetwork information. For example if you want to
save the SCOTUS subnetwork then create a folder called *data/clean/scotus/*
which contains the case_metadata.csv and edgelist.csv files for the SCOTUS
subnetwork.

Other data, such as the [bag-of-words](https://en.wikipedia.org/wiki/Bag-of-words_model) representation of the opinions should go into jurisdiction subfolders e.g. *clean/scotus/opinions/* might contain .json files for each opinion that store the bag of words representation.

You can populate the clean/ folder using functions in *make_clean_data.py* that is in the code/pipline/ folder.

Note that the title *clean* is not meant to create the illusion that the data in this actually *clean*. We did our best.
