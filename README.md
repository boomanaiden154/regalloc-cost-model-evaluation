### Running Scripts

```
mkdir testing
cd testing
/regalloc-testing/scripts/test_file.sh /regalloc-testing/benchmarks/fannkuch-redux.c
```

All of the results should be placed in a `results.txt` file in the same directory.
Once you have the `results.txt` file, you can also use the `evaluate_no_weights.py`
script to automatically evaluate how well the model performed in terms of the
average absolute difference between the regalloc score and the actual performance
relative to the baseline and in terms of how often if correctly found the polarity.

```
python3 /reglloc-testing/scripts/evaluate_no_weights.py results.txt
```

This will print the calculated information out to STDOUT.


### Building the Docker Image

The docker image that is described in `Dockerfile` contains all the tooling
need to run all the experiments within this repository. To build it, you
also need the [ml-compiler-opt](https://github.com/google/ml-compiler-opt)
repository checked out. Build the development docker image in that repository,
following the instructions in `experimental/docker/README.md`. This will give
an image tagged `mlgo-development`. Then you can build the Docker image
present in this repository:

```
cd /path/to/regalloc-cost-model-evaluation
docker build -t regalloc-cost-model-evaluation .
```

This will take a while and consume quite a bit of disk space as it does
quite a few things to set up a development environment that allows for
a lot of experimentation.