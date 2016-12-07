# law-net
What can we learn by applied network analysis to the law? This project contains code to analyze the law case citation network using data generously provided by [CourtListener](https://www.courtlistener.com/). You will find code that creates the pipeline that takes data from CourtListener and creates various citation networks such as

- entire law case citation network (this is ~3 million nodes and ~30 million edges)
- SCOTUS subnetwork (e.g. both the citing case and cited case are SCOTUS cases)
- jurisdiction network

Note that 'entire' does not actually mean we have every court case. We are still figuring out how good our coverage is and will post updates when we have more.

To get started with the data see [getting_started.ipynb](https://github.com/idc9/law-net/blob/master/getting_started.ipynb). User beware: we have not yet make the code clean/robust/user friendly/pleasant/etc -- we will get to this soon.

If you are interested in collaborating feel free to reach out to us!


This is a collaboration between

[Brendan Schneiderman](https://www.linkedin.com/in/brendan-schneiderman-150b1375)

[Iain Carmichael](http://iaincarmichael.web.unc.edu/)

[James Jushchuk](https://www.linkedin.com/in/james-jushchuk-358754115)

[James Wudel](https://www.linkedin.com/in/jwudel)

[Michael Kim](https://www.linkedin.com/in/michael-kim-76aa53104)

[Shankar Bhamidi](http://shankarbhamidi.web.unc.edu/)
