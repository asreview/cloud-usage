# asreview-cloud (Running simulations on the cloud and/or in parallel)

This repository houses some files to help run simulations on the cloud, i.e., outside your computer, possibly in parallel.
We assume that you know how to run simulations on your computer using [Makita](https://github.com/asreview/asreview-makita).
The information for running simulations on the cloud is separated in the following use cases:

- [Running a "short" simulation on SURF, Digital Ocean, AWS, Azure, etc.](10-simple.md)
  - Use this guide if your local computer is not powerful enough, or if you need it available while the simulations run.
- [Running simulations in parallel](20-parallel.md)
  - Use this when you have a computer (local or remote) with a good amount of cores and memory, and you want to speed things up.
- [Running many jobs.sh files one after the other](30-many-jobs.md)
  - Use if you need to run many simulations changing parameteres, but you only have one computer.
  - You can still parallelize the individual `jobs.sh` execution.
- [Running large simulations using Kubernetes](40-kubernetes.md)
  - Use if your simulation would take a very long time.
  - Alternatively, if you have a powerfull enough computer and needs to control the cpu and memory usage.
  - This is very complicated and it usually requires a lot of time to setup and money to run on a cluster.
