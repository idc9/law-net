# law-net
What can we learn by applying network and text analysis to the law? This project contains code to analyze legal text and citation networks using data generously provided by [CourtListener](https://www.courtlistener.com/) and the [Supreme Court Database](http://scdb.wustl.edu/).

Some interesting networks include

- Supreme Court citation network (27,885 nodes, 234,312 directed edges)
- Federal Appellate circuit (959,985 nodes, 6,649,916 directed edges)
- any one of the over [400 jurisdiction](https://www.courtlistener.com/coverage/) subnetworks listed on CourtListener

These all have accompanying opinion text files as well as additional node metadata such as the case date and hand coded issue area (for SCOTUS).

We recently gave a presentation about our exploratory analysis at the [PyData](http://pydata.org/carolinas2016/) conference.

https://www.youtube.com/watch?v=AP7_godzwVI


You can load the SCOTUS subnetwork (saved in this directory as a .graphml file)
```
import igraph
G = Graph.Read_GraphML('scotus_network.graphml')
```

# Our code

User beware: we have not yet make the code clean/robust/user friendly/pleasant/etc -- we will get to this soon. If you have trouble with something please reach out to Iain (iain@unc.edu).

To download much more data see [download_data.ipynb](https://github.com/idc9/law-net/blob/master/download_data.ipynb). This notebook allows you to work with other jurisdiction subnetworks and the opinion text files. Note the two directories you have to change at the top of the notebook.

One of the functions in download_data.ipynb will set up a data directory. I suggest putting `data_dir` outside your copy of the github repo or Dropbox. Github doesn't like large data files and Dropbox might slow things down if you do a lot of reading and writing (i.e. for some NLP operations).



## About the data
Current we are using data from [CourtListener](courtlistener.com)  (CL) and the [Supreme Court Data Base](http://scdb.wustl.edu/) (SCDB)
- the citation network comes from CL
- opinion texts come from CL
- some case metadata (jurisdiction, data, judges) comes from CL
- additional case meta data comes from SCDB
    - for `issueArea` we have coded Missing as 0. Only SCOTUS cases can have issueArea.

- we identify cases by their CourtListener **opinion** id
    - CL opinion ids and cluster ids are **not** necessarily the same. One cluster can have many opinions.



If you are interested in collaborating feel free to reach out to us! This is a collaboration between

[Brendan Schneiderman](https://www.linkedin.com/in/brendan-schneiderman-150b1375)

[Iain Carmichael](http://iaincarmichael.web.unc.edu/)

[James Jushchuk](https://www.linkedin.com/in/james-jushchuk-358754115)

[James Wudel](https://www.linkedin.com/in/jwudel)

[Michael Kim](https://www.linkedin.com/in/michael-kim-76aa53104)

[Shankar Bhamidi](http://shankarbhamidi.web.unc.edu/)
