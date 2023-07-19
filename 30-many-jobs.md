# Running many jobs.sh files one after the other

One more advanced situation is running many simulations that have changing parameters.
For instance, simulating different combinations of models.

Ideally, you would want to parallelize even more your execution, but this guide assumes that you can't do that, for instance, because you don't have access to more computers.

In that case, the guidance that we can provide is to recommend writing a loop over the arguments, and properly saving the output.

Let's assume that you want to run `asreview makita CONSTANT VARIABLE` where `CONSTANT` is a fixed part that is the same for all runs and `VARIABLE` is what you are varying.

## Arguments

Open a file `makita-args.txt` and write the arguments that you want to run.
For instance, we could write

```plaintext
-m logistic -e tfidf
-m nb -e tfidf
```

## Execution script

Now, download the file `many-jobs.sh`:

```bash
wget https://raw.githubusercontent.com/abelsiqueira/asreview-cloud/main/many-jobs.sh
```

This file should contain something like

```bash
CONSTANT="template arfi" # Edit here to your liking
num_cores=$1

# Shortened for readability

while read -r arg
do
  # A overwrites all files
  echo "A" | asreview makita "$CONSTANT" "$arg"
  # Edit to your liking from here
  python3 split-file.py jobs.sh
  bash parallel_run.sh "$num_cores"
  mv output "output-args_$arg"
  # to here
done < makita-args.txt
```

Edit this file to reflect your usage:

1. The `CONSTANT` variable defines that we will run `template arfi` for every `asreview makita` call. If you use a custom template, change here.

2. After running `asreview makita`, we chose to use the [parallelization strategy](20-parallel.md). If you prefer, you can use just `bash jobs.sh` instead of these two first lines. The last line renames the output, so it is important, but you do something else that you find more relevant, such as uploading the results.

## Running

After you change everything that needs changing, simply run

```bash
bash many-jobs.sh NUMBER_OF_CORES
```
