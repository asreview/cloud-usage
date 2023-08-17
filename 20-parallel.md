# Running the jobs.sh file with GNU parallel

These steps can be run locally or in a remote computer.
However, given the nature of this parallelization, there are no limitation to memory usage, so your local computer can run out of memory.

If you run this method in a remote computer, follow the [guide on running simulations remotely first](10-simple.md).
When that guide tell you to run your simulations, stop and come back here.

## Install GNU parallel

Install the package [GNU parallel](https://www.gnu.org/software/parallel/) following the instructions on the website.
We recommend installing the package via package managers if you have one (such as `apt-get`, `homebrew` or `chocolatey`).

> **Note**
>
> For SURF, that would be `sudo apt-get install parallel`.

In case you do not have one, you can follow the steps below:

- If you are using UNIX based system(Linux or MacOS),you are going to need `wget`.

Run those commands `parallel-*` will be a downloaded file with a number instead of '*':

```bash
wget https://ftp.gnu.org/gnu/parallel/parallel-latest.tar.bz2
tar -xjf parallel-latest.tar.bz2
cd parallel-NUMBER
./configure
make
sudo make install
```

Check that the package is installed with

```bash
parallel --version
```

## Running jobs.sh in parallel

To parallelize your `jobs.sh` file, we need to split it into blocks that can be parallelized.
To do that, we need the [split-file.py](code/split-file.py) script included in this repo.

To directly download it from the internet, you can issue the following command:

```bash
wget https://raw.githubusercontent.com/asreview/cloud-usage/main/code/split-file.py
```

Now run the following to split on the jobs.sh file into three files:

```bash
python3 split-file.py jobs.sh
```

This will generate files `jobs.sh.part1`, 2, and 3.
The first part contains all lines with "mkdir" and "describe" in them.
The second part contains all lines with "simulate" in them.
The rest of the useful lines (non-empty and not comments) constitute the third part.

Each part must finish before the next is run, and the first part must be run sequentially.
The other two parts can be run using `parallel`.

To simplify your usage, we have created the script [parallel_run.sh](code/parallel_run.sh).
Download it issuing

```bash
wget https://raw.githubusercontent.com/asreview/cloud-usage/main/code/parallel_run.sh
```

Then you can just run the script below, specifying the number of cores as an argument.
> **Warning**
> We recommend not using all of your CPU cores at once.
> Leave at least one or two to allow your machine to process other tasks.
> Notice that there is no limitation on memory usage per task, so for models that use a lot of memory, there might be some competition for resources.

```bash
bash parallel_run.sh NUMBER_OF_CORES
```
