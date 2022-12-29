To run the scripts:

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
