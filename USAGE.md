# Examples of usage

In this file, we will try to discuss a few common usages and what modifications would be necessary to achieve them.
If necessary, extra files will be provide in the folder [examples](examples).
Be sure to read the [README](README.md) first.
This file only supplements the README and it is not supposed to be enough to quickstart.

By the way, if you are only testing and don't have a data set yet, you can download one from [asreview-makita](https://raw.githubusercontent.com/asreview/asreview-makita/main/examples/arfi_example/data/ptsd.csv) using `wget`:

```bash
wget https://raw.githubusercontent.com/asreview/asreview-makita/main/examples/arfi_example/data/ptsd.csv
```

## Provide only data and run makita on the cloud

This is the default usage inside the `tasker.sh`.
You only need to:

- Create a folder `data` with your `.csv` files.
- Modify `tasker.sh` to run the makita template that you want. (Search for `asreview makita`). The default execution is ARFI.
- If necessary, modify `worker.Dockefile` to install more packages.

## Custom ARFI (different models) and synergy data

The files inside [examples/custom_arfi_synergy](examples/custom_arfi_synergy/) will allow you to run all data in the Synergy dataset and pass specific classifiers and feature extractors.

Copy the files there to the root:

```bash
cp -f examples/custom_arfi_synergy/* .
```

Then, modify `SETTINGS` in `tasker.sh` to your liking.

> **Note**
>
> Since this model runs all files, it is advisable to test the execution with a single simulate call from each file.
> To do that, run `cp custom_arfi.txt.template.test custom_arfi.txt.template` before building your images.
> It might also help to remove the larger files Brouwer_2019.csv and Walker_2018csv.

### More details

The `custom_arfi.txt.template` file has the following modifications from the basic ARFI template:

- it adds an argument `SETTINGS_PLACEHOLDER` to the simulate call.
- it runs `simulate`, `metrics`, and then removes the `.asreview` project file in a single execution. This is done to avoid filling up the disk with `.asreview` files.
- it does not produce a plot, because the `.asreview` files and not present anymore.

The `tasker.sh` introduces a bash variable `SETTINGS`, which defaults to empty.
If you want to pass a different classifiers and/or feature extractor, change this variable.
An example is given. Then, Makita is called with the template argument to create a `jobs.sh` file with the `SETTINGS_PLACEHOLDER` argument.
Finally, using `sed`, we substitute the `SETTINGS_PLACEHOLDER` by the value of the `SETTINGS` variable.

The `worker.Dockerfile` updates Makita and adds more packages to support extra models.

The `tasker.Dockerfile` install the synergy dataset and downloads all files into the `/app/data` folder.
