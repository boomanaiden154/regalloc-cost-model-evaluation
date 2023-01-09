# Multisample Evaluation

The code used to generate the data/results shown here is from commit
`8704d02ba2a1c770d456c39a787c3df48050a182`.

### My Setup

For my setup I am running two Intel Sandy Bridge CPUs (Xeon E5-2670) with
hyperthreading disabled to avoid any possible effects there. I set the
`isolcpus` flag on my kernel to `0,1,2,3,4,5,6,7,8,9,10,11` to prevent the
scheduler from placing anything on those cores so I could later use them
for benchmarking without running into any effects produced by the process
scheduler.

Using `cpupower` I set the clock speed of all the cores to 1200MHz to
avoid any possible benchmarking artifacts from automatic clock frequency
scaling.

### Running the experiments

I collected all of my data by using two multi-sample tests with data created
from the `nbody.c` script with all functions inlined to avoid having to deal
with effects from function calls (setting `-DALWAYS_INLINE` in the compiler
invocation). After starting the docker image present in the repositorr
(make sure to start it with the instructions present in `README.md`,
particularly noting the `--privileged` flag in the `docker run`
invocation), we can start collecting data from within the container.
First, set up some environment variables:

```bash
export EXTRA_FLAGS=-DALWAYS_INLINE
export THREAD_COUNT=12
```

I chose `THREAD_COUNT` to be 12 given that I set `isolcpus` to isolate
the first 12 cores that I have. Then, the actual data collection:

```bash
mkdir /testing-multiple
cd /testing-multiple
/regalloc-testing/scripts/multiple/test_multiple.sh /regalloc-testing/benchmarks/nbody.c
mkdir /testing-multiple2
cd /testing-multiple2
/regalloc-testing/scripts/multiple/test_multiple.sh /regalloc-testing/benchmarks/nbody.c
```

The `test_multiple.sh` invocations will take a long time because by default
they each do 930 iterations of PGO compilation and benchmarking.

### Processing the data

I used several scripts within the repository to process the data. First of all,
it's helpful to have concatenated raw regalloc (raw counts of copies/loads/
stores/etc weighted by MBB frequency scoring data. To grab this:

```bash
cd /testing-multiple
/regalloc-testing/scripts/multiple/combined_regalloc_raw_multiple.sh
/regalloc-testing/scripts/multiple/combined_regalloc.sh test-combined.txt test-combined.txt
cd /testing-multiple2
/regalloc-testing/scripts/multiple/combined_regalloc_raw_multiple.sh
/regalloc-testing/scripts/multiple/combined_regalloc.sh test-combined.txt test-combined.txt
```

Then we can fit weights to the first sample:

```bash
cd /testing-multiple
python3 /regalloc-testing/scripts/fit_weights.py --input_file=./test-combined.txt
```

Which gives the following with what I ended up with:

```
Multivariable regression coefficients:[ 0.1514095   0.22855899 -0.56732352 -0.13465734  0.        ]
Multivariable regression intercept:2023054089.4567916
Normalized coefficients:[1.0, 1.5095419411083808, -3.7469479081565433, -0.8893585852276341, 0.0]
Unadjusted R^2 value:0.1317648313848896
Post regression polarity correct:671
Post regression average difference:0.016195655093246063
```

Fitting weights to the second sample:

```bash
cd /testing-multiple2
python3 /regalloc-testing/scripts/fit_weights.py --input_file=./test-combined.txt
```

results in the following with what I got:

```
Multivariable regression coefficients:[0.80959483 0.39649935 0.47888509 0.49964127 0.        ]
Multivariable regression intercept:1209410464.6733084
Normalized coefficients:[0.9999999999999999, 0.4897503468356181, 0.591512040865649, 0.617149773503729, 0.0]
Unadjusted R^2 value:0.3691650827417813
Post regression polarity correct:871
Post regression average difference:0.027770976493531475
```

Comparing the normalized coefficients, we can see that they're quite different,
and also not really what would be expected (especially for the second run, 
copies being way more expensive than loads? Stores also being more expensive
than loads?).

To validate these findings and make sure they we aren't being susceptible to
random noise and run to run variations, we should also make sure that some of
the individual samples within the sample groups are repeatable to a reasonable
degree. There is tooling in this repository to do this. For example, let's
check the first and last iteration of each sample group:

```bash
mkdir /testing-multiple-control && cd /testing-multiple-control
mkdir group1-iteration1 && cd group1-iteration1
/regalloc-testing/scripts/test_file_existing_compiles.sh /testing-multiple/iteration-1
cd ..
mkdir group1-iteration30 && cd group1-iteration30
/regalloc-testing/scripts/test_file_existing_compiles.sh /testing-multiple/iteration-30
cd ..
mkdir group2-iteration1 && cd group2-iteration1
/regalloc-testing/scripts/test_file_existing_compiles.sh /testing-multiple2/iteration-1
cd ..
mkdir group2-iteration30 && cd group2-iteration30
/regalloc-testing/scripts/test_file_existing_compiles.sh /testing-multiple2/iteration-30
```

Now, let's look at the outputs from each of these and compare them to the
original samples:

For `group1-iteration1`:

```bash
cd /testing-multiple-control/group1-iteration1
/regalloc-testing/scripts/combined_regalloc_raw.sh test-combined.sh
python3 /regalloc-testing/scripts/fit_weights.py --input_file=test-combined.txt
```

Which results in:
```
Multivariable regression coefficients:[ 0.10237747  0.49548383 -0.9866447   0.75451635  0.        ]
Multivariable regression intercept:1929525244.1100466
Normalized coefficients:[1.0, 4.839773907955084, -9.63732213881887, 7.369944949764378, 0.0]
Unadjusted R^2 value:0.3036027695259891
Post regression polarity correct:20
Post regression average difference:0.014179073681918031
```

Compared to the original in the sample group:

```bash
python3 /regalloc-testing/scripts/fit_weights.py --input_file=/testing-multiple/iteration-1/test-combined.txt
```

Which results in:

```
Multivariable regression coefficients:[ 0.1133384   0.66932778 -1.10976041  0.49018797  0.        ]
Multivariable regression intercept:1790207385.355023
Normalized coefficients:[1.0, 5.905569561275844, -9.791566171780042, 4.324994785535641, 0.0]
Unadjusted R^2 value:0.26119049654116866
Post regression polarity correct:24
Post regression average difference:0.015891405727666008
```

As we can see, the values don't line up perfectly (and definitely line up a lot
worse than what I would like), but the values are a lot closer to each other
than what we would expect/what we see in sample to sample differences. I'm
going to include data for the other three comparison tests in a truncated
format since the commands are the exact same (the new control test output
comes first and the original sample output is second):

For `group1-iteration30`:

```
Multivariable regression coefficients:[ 0.26221871  0.5859754  -1.4855566  -1.11857495  0.        ]
Multivariable regression intercept:2068245307.725257
Normalized coefficients:[1.0, 2.2346818705869875, -5.665334039856376, -4.265809018278413, 0.0]
Unadjusted R^2 value:0.4565897459920699
Post regression polarity correct:18
Post regression average difference:0.007955393997135952
```

```
Multivariable regression coefficients:[ 0.26668226  0.48945733 -1.06730069 -0.18985471  0.        ]
Multivariable regression intercept:1904034233.253926
Normalized coefficients:[1.0, 1.8353576160365521, -4.002143482605114, -0.7119135099919597, 0.0]
Unadjusted R^2 value:0.35040617422008746
Post regression polarity correct:23
Post regression average difference:0.0085326127035947
```

For `group2-iteration1`:

```
Multivariable regression coefficients:[1.02194486 0.14512875 0.57642976 2.70950706 0.        ]
Multivariable regression intercept:1120720407.0325546
Normalized coefficients:[1.0, 0.14201231307119322, 0.5640517248876316, 2.6513241281366846, 0.0]
Unadjusted R^2 value:0.7286189600075257
Post regression polarity correct:25
Post regression average difference:0.014554374734731071
```

```
Multivariable regression coefficients:[1.08056092 0.10422116 0.46206789 2.6210175  0.        ]
Multivariable regression intercept:1142988138.4027019
Normalized coefficients:[1.0, 0.09645097690115961, 0.4276185472445662, 2.4256082672147614, 0.0]
Unadjusted R^2 value:0.750051603451299
Post regression polarity correct:25
Post regression average difference:0.013949799248037053
```

For `group2-iteration30`:

```
Multivariable regression coefficients:[ 0.5298814   0.6107433   0.48008735 -1.06823167  0.        ]
Multivariable regression intercept:1296206445.15168
Normalized coefficients:[1.0, 1.152603758079358, 0.9060279270906135, -2.015982552197673, 0.0]
Unadjusted R^2 value:0.4195753152439843
Post regression polarity correct:25
Post regression average difference:0.012802122755349813
```

```
Multivariable regression coefficients:[ 0.49508183  0.54261693  0.43054614 -0.70382139  0.        ]
Multivariable regression intercept:1343645469.9878192
Normalized coefficients:[1.0, 1.0960146415822214, 0.8696464264905663, -1.4216263840274397, 0.0]
Unadjusted R^2 value:0.36608785956622414
Post regression polarity correct:24
Post regression average difference:0.014373357256543788
```

So the repeatability of all these numbers is alright, but definitely not
perfect. The results for repeating a sample are still significantly more
similar than the results for two different samples, and the model from one
repeat should perform similarly well on another repeat (maybe provide some
analysis to back up this claim?).

Now, let's look at how the optimal linear model from one sample group works
on the other sample group and how a combined model fares on both of the
individual samples.

Getting the optimal coefficients for the first sample group and testing it
on the second sample group:

```bash
cd /testing-multiple
python3 /regalloc-testing/scripts/fit_weights.py --input_file=test-combined.txt --output=cofintnolbr
# Output of the above is 0.1514095023746417 0.22855899411687064 -0.5673235181976869 -0.13465734082193145 0.0 2023054089.4567916
cd /testing-multiple2
python3 /regalloc-testing/scripts/evaluate_weights.py 0.1514095023746417 0.22855899411687064 -0.5673235181976869 -0.13465734082193145 0.0 2023054089.4567916 test-combined.txt
```

Which gives the following output:

```
polarity correct:903/929
average difference:0.04282104956813861
```

Going in the reverse direction:
```bash
cd /testing-multiple2
python3 /regalloc-testing/scripts/fit_weights.py --input_file=test-combined.txt --output=cofintnolbr
# Output of the above is 0.8095948290842067 0.3964993483403132 0.4788850896258754 0.49964126539910836 0.0 1209410464.6733084
cd /testing-multiple
python3 /regalloc-testing/scripts/evaluate_weights.py 0.8095948290842067 0.3964993483403132 0.4788850896258754 0.49964126539910836 0.0 1209410464.6733084 test-combined.txt
```

Which gives the following output:
```
polarity correct:311/929
average difference:0.03317628639902063
```

And then the combined model:
```bash
cd /
cat /testing-multiple/test-combined.txt > test-combined.txt
cat /testing-multiple2/test-combined.txt >> test-ccombined.txt
python3 /regalloc-testing/scripts/fit_weights.py --input_file=test-combined.txt --output=cofintnolbr
# Output of the above is 0.3039412698271154 0.3146090443909967 -0.5151634266701539 -0.007120739834068272 0.0 1767102673.1120062
cd /testing-multiple
python3 /regalloc-testing/scripts/evaluate_weights.py 0.3039412698271154 0.3146090443909967 -0.5151634266701539 -0.007120739834068272 0.0 1767102673.1120062 test-combined.txt
cd /testing-multiple2
python3 /regalloc-testing/scripts/evaluate_weights.py 0.3039412698271154 0.3146090443909967 -0.5151634266701539 -0.007120739834068272 0.0 1767102673.1120062 test-combined.txt
```

Output from `evaluate_weights.py` in `/testing-multiple`:

```
polarity correct:538/929
average difference:0.01858380050695964
```

Output from `evaluate_weights.py` in `/testing-multiple2`:

```
polarity correct:906/929
average difference:0.03757900624883771
```

We can also look at heat maps of each sample group to see how the model
produced from an individual sample performs on all the other samples in the
sample group. For `/testing-multiple`:

```bash
cd /testing-multiple
/regalloc-testing/scripts/multiple/fit_weights_extraction.sh cofintnolbr cofints.txt
PYTHONPATH="/regalloc-testing/scripts" python3 /regalloc-testing/scripts/multiple/sample_weight_performance_matrix.py --params_file=cofints.txt --is_csv=true
```

This results in the following matrix (the ith row is the model produced by the
ith sample within the group and the jth column is the performance of the model
on the jth sample as indicated by the metric number of binaries/benchmarks where
the polarity is correct over the the total number of binaries/benchmarks):

```
0.80,0.17,0.67,0.40,0.33,0.73,0.73,0.77,0.63,0.57,0.67,0.20,0.43,0.60,0.50,0.63,0.90,0.47,0.60,0.63,0.87,0.27,0.50,0.50,0.53,0.90,0.57,0.73,0.10,0.63
0.87,0.73,0.63,0.43,0.90,0.43,0.77,0.77,0.60,0.53,0.80,0.60,0.43,0.73,0.40,0.50,0.60,0.30,0.27,0.47,0.73,0.53,0.07,0.57,0.70,0.67,0.57,0.80,0.27,0.37
0.50,0.17,0.80,0.43,0.23,0.47,0.63,0.77,0.70,0.47,0.50,0.70,0.47,0.57,0.27,0.70,0.77,0.30,0.70,0.53,0.57,0.67,0.47,0.70,0.50,0.80,0.67,0.80,0.37,0.83
0.83,0.30,0.57,0.53,0.80,0.27,0.67,0.77,0.63,0.50,0.73,0.33,0.23,0.70,0.33,0.50,0.20,0.23,0.30,0.40,0.53,0.20,0.13,0.83,0.67,0.57,0.53,0.73,0.40,0.47
0.77,0.17,0.73,0.40,0.50,0.30,0.73,0.77,0.63,0.57,0.67,0.20,0.27,0.73,0.20,0.57,0.47,0.30,0.57,0.53,0.57,0.20,0.20,0.83,0.63,0.83,0.53,0.80,0.40,0.70
0.80,0.17,0.67,0.40,0.33,0.57,0.73,0.77,0.63,0.57,0.70,0.50,0.30,0.70,0.40,0.63,0.77,0.43,0.57,0.60,0.77,0.37,0.20,0.67,0.53,0.90,0.60,0.77,0.13,0.73
0.83,0.17,0.70,0.40,0.43,0.47,0.73,0.77,0.63,0.53,0.70,0.17,0.30,0.67,0.37,0.60,0.50,0.37,0.50,0.47,0.73,0.17,0.20,0.73,0.57,0.83,0.57,0.80,0.30,0.63
0.77,0.17,0.77,0.40,0.37,0.37,0.77,0.77,0.63,0.60,0.67,0.20,0.33,0.77,0.30,0.57,0.53,0.33,0.60,0.53,0.63,0.23,0.23,0.80,0.50,0.87,0.60,0.80,0.27,0.73
0.83,0.30,0.60,0.53,0.73,0.30,0.70,0.77,0.63,0.50,0.70,0.33,0.23,0.67,0.37,0.53,0.20,0.27,0.30,0.43,0.57,0.20,0.13,0.83,0.67,0.57,0.53,0.73,0.40,0.43
0.63,0.83,0.27,0.57,0.83,0.63,0.50,0.63,0.50,0.47,0.67,0.33,0.60,0.57,0.70,0.40,0.43,0.80,0.27,0.53,0.60,0.23,0.47,0.33,0.53,0.27,0.37,0.33,0.43,0.20
0.73,0.30,0.67,0.40,0.60,0.37,0.77,0.73,0.63,0.57,0.77,0.70,0.47,0.70,0.27,0.53,0.70,0.37,0.60,0.47,0.63,0.63,0.17,0.73,0.60,0.67,0.60,0.80,0.30,0.57
0.50,0.17,0.73,0.40,0.20,0.70,0.73,0.77,0.63,0.43,0.50,0.53,0.43,0.60,0.47,0.67,0.93,0.43,0.67,0.60,0.77,0.43,0.57,0.57,0.43,0.87,0.63,0.77,0.20,0.73
0.77,0.17,0.70,0.40,0.27,0.53,0.77,0.77,0.63,0.53,0.70,0.17,0.27,0.73,0.43,0.60,0.60,0.33,0.53,0.57,0.67,0.20,0.37,0.70,0.57,0.83,0.60,0.77,0.23,0.77
0.83,0.17,0.80,0.40,0.43,0.33,0.73,0.77,0.63,0.57,0.67,0.27,0.30,0.77,0.33,0.57,0.60,0.37,0.60,0.53,0.67,0.23,0.20,0.80,0.60,0.87,0.60,0.80,0.27,0.63
0.70,0.67,0.70,0.40,0.73,0.57,0.73,0.73,0.63,0.57,0.57,0.83,0.53,0.70,0.23,0.57,0.87,0.33,0.43,0.47,0.80,0.67,0.10,0.50,0.50,0.57,0.70,0.67,0.20,0.47
0.83,0.17,0.67,0.43,0.50,0.60,0.73,0.77,0.63,0.57,0.73,0.13,0.30,0.63,0.57,0.57,0.67,0.43,0.47,0.60,0.83,0.13,0.33,0.53,0.60,0.80,0.47,0.73,0.20,0.53
0.77,0.13,0.57,0.53,0.43,0.47,0.70,0.73,0.70,0.53,0.67,0.03,0.27,0.60,0.53,0.57,0.33,0.33,0.47,0.60,0.57,0.13,0.40,0.73,0.53,0.77,0.40,0.70,0.37,0.63
0.57,0.17,0.73,0.40,0.20,0.60,0.70,0.77,0.63,0.43,0.47,0.57,0.47,0.63,0.37,0.67,0.90,0.43,0.70,0.67,0.70,0.43,0.53,0.57,0.40,0.97,0.60,0.77,0.20,0.73
0.37,0.23,0.77,0.43,0.30,0.57,0.53,0.40,0.67,0.50,0.37,0.87,0.60,0.50,0.33,0.63,0.83,0.37,0.73,0.60,0.60,0.77,0.57,0.57,0.43,0.73,0.70,0.80,0.43,0.70
0.80,0.37,0.63,0.43,0.40,0.80,0.73,0.77,0.63,0.60,0.53,0.43,0.43,0.63,0.63,0.60,0.93,0.57,0.53,0.73,0.87,0.30,0.43,0.30,0.53,0.87,0.53,0.70,0.07,0.57
0.83,0.17,0.73,0.40,0.37,0.50,0.73,0.77,0.63,0.57,0.70,0.17,0.30,0.67,0.40,0.60,0.60,0.43,0.50,0.60,0.70,0.13,0.33,0.70,0.57,0.83,0.53,0.80,0.27,0.63
0.80,0.17,0.63,0.40,0.60,0.50,0.77,0.77,0.63,0.53,0.70,0.20,0.30,0.77,0.53,0.53,0.57,0.40,0.47,0.57,0.80,0.13,0.27,0.60,0.60,0.77,0.40,0.77,0.23,0.47
0.87,0.17,0.70,0.40,0.27,0.57,0.73,0.77,0.63,0.50,0.70,0.20,0.33,0.67,0.43,0.67,0.83,0.40,0.67,0.53,0.80,0.30,0.37,0.60,0.43,0.90,0.60,0.77,0.23,0.77
0.83,0.17,0.67,0.40,0.33,0.63,0.70,0.77,0.63,0.57,0.70,0.23,0.33,0.73,0.43,0.63,0.80,0.47,0.63,0.53,0.83,0.27,0.30,0.63,0.50,0.87,0.60,0.77,0.17,0.73
0.73,0.17,0.77,0.40,0.37,0.37,0.77,0.77,0.63,0.40,0.73,0.50,0.30,0.73,0.30,0.67,0.73,0.37,0.60,0.60,0.70,0.37,0.30,0.73,0.50,0.87,0.67,0.77,0.27,0.77
0.60,0.17,0.70,0.40,0.10,0.70,0.77,0.73,0.67,0.43,0.57,0.17,0.40,0.50,0.50,0.63,0.87,0.47,0.63,0.57,0.67,0.30,0.63,0.57,0.47,0.90,0.57,0.73,0.30,0.77
0.80,0.17,0.67,0.40,0.37,0.53,0.73,0.77,0.63,0.60,0.67,0.20,0.33,0.73,0.40,0.57,0.67,0.43,0.53,0.53,0.73,0.20,0.27,0.70,0.57,0.87,0.57,0.73,0.17,0.73
0.80,0.17,0.70,0.40,0.53,0.37,0.73,0.77,0.63,0.53,0.77,0.60,0.30,0.77,0.33,0.53,0.67,0.40,0.57,0.53,0.73,0.40,0.23,0.80,0.63,0.83,0.60,0.80,0.20,0.63
0.53,0.17,0.67,0.43,0.37,0.23,0.57,0.70,0.67,0.37,0.63,0.67,0.30,0.60,0.27,0.63,0.33,0.20,0.60,0.50,0.53,0.53,0.40,0.83,0.67,0.63,0.67,0.77,0.47,0.73
0.83,0.17,0.67,0.40,0.40,0.47,0.73,0.77,0.63,0.60,0.67,0.20,0.33,0.70,0.33,0.60,0.67,0.43,0.57,0.53,0.77,0.27,0.20,0.73,0.57,0.93,0.60,0.80,0.17,0.77
```

Which looks like the following in heatmap form:

![testing-multiple heatmap](data:image/png;base64,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)

Doing the same for `/testing-multiple2`:

```bash
cd /testing-multiple2
/regalloc-testing/scripts/multiple/fit_weights_extraction.sh cofintnolbr cofints.txt
PYTHONPATH="/regalloc-testing/scripts" python3 /regalloc-testing/scripts/multiple/sample_weight_performance_matrix.py --params_file=cofints.txt --is_csv=true
```

The outputted matrix:

```
0.83,0.97,0.70,0.93,1.00,0.50,0.63,0.80,0.73,0.40,0.67,0.70,0.90,0.83,0.60,0.50,0.57,0.73,0.77,0.47,0.33,0.77,0.43,0.73,0.67,0.70,0.80,0.73,0.83,0.50
0.73,0.97,0.80,0.90,1.00,0.63,0.70,0.67,0.63,0.47,0.63,0.70,0.87,0.87,0.80,0.73,0.47,0.77,1.00,0.63,0.63,0.80,0.43,0.73,0.93,0.67,0.80,0.73,0.77,0.60
0.63,0.97,0.73,0.87,0.97,0.57,0.70,0.77,0.60,0.57,0.80,0.70,0.87,0.73,0.77,0.83,0.53,0.87,1.00,0.63,0.37,0.83,0.47,0.77,0.77,0.63,0.80,0.70,0.83,0.63
0.87,0.93,0.63,0.97,0.90,0.43,0.60,0.63,0.70,0.30,0.73,0.60,0.80,0.70,0.43,0.50,0.67,0.67,1.00,0.57,0.17,0.73,0.40,0.63,0.13,0.67,0.90,0.60,0.57,0.70
0.83,0.97,0.70,0.93,1.00,0.67,0.67,0.87,0.63,0.47,0.70,0.70,0.90,0.83,0.63,0.53,0.57,0.73,0.77,0.50,0.33,0.77,0.47,0.77,0.73,0.73,0.80,0.73,0.80,0.47
0.87,0.73,0.70,0.60,0.93,0.60,0.73,0.53,0.60,0.43,0.40,0.60,0.83,0.83,0.27,0.20,0.37,0.77,0.23,0.43,0.57,0.67,0.43,0.73,0.80,0.67,0.80,0.70,0.70,0.47
0.80,0.97,0.77,0.83,1.00,0.63,0.73,0.63,0.63,0.40,0.57,0.70,0.90,0.90,0.53,0.57,0.67,0.83,0.80,0.70,0.37,0.80,0.47,0.70,0.77,0.70,0.80,0.67,0.73,0.73
0.83,0.97,0.77,0.93,0.97,0.67,0.67,0.73,0.63,0.40,0.80,0.73,0.87,0.80,0.70,0.80,0.70,0.80,1.00,0.67,0.27,0.80,0.43,0.73,0.60,0.63,0.83,0.73,0.77,0.67
0.73,0.97,0.73,0.93,0.90,0.67,0.70,0.80,0.57,0.60,0.80,0.73,0.83,0.80,0.73,0.77,0.70,0.77,1.00,0.80,0.30,0.77,0.53,0.67,0.70,0.63,0.83,0.63,0.80,0.77
0.43,0.90,0.37,0.87,0.77,0.57,0.73,0.70,0.60,0.60,0.80,0.73,0.90,0.47,0.77,0.90,0.37,0.57,0.93,0.57,0.47,0.80,0.50,0.60,0.50,0.70,0.63,0.77,0.63,0.50
0.77,0.73,0.77,0.93,0.73,0.60,0.60,0.70,0.53,0.57,0.80,0.60,0.77,0.77,0.70,0.80,0.70,0.77,1.00,0.70,0.23,0.73,0.50,0.67,0.43,0.63,0.83,0.60,0.80,0.90
0.77,0.97,0.77,0.90,0.93,0.67,0.70,0.80,0.60,0.53,0.83,0.73,0.90,0.80,0.73,0.77,0.70,0.77,1.00,0.70,0.30,0.80,0.53,0.77,0.67,0.63,0.83,0.70,0.80,0.70
0.73,0.97,0.77,0.93,0.97,0.63,0.70,0.83,0.63,0.43,0.80,0.73,0.87,0.80,0.80,0.70,0.60,0.77,1.00,0.77,0.37,0.83,0.47,0.70,0.77,0.63,0.80,0.67,0.80,0.77
0.87,0.97,0.70,0.93,1.00,0.53,0.67,0.63,0.73,0.43,0.47,0.70,0.90,0.93,0.53,0.33,0.50,0.80,0.67,0.43,0.37,0.73,0.40,0.77,0.80,0.73,0.80,0.67,0.77,0.50
0.67,0.97,0.80,0.80,0.90,0.60,0.70,0.57,0.50,0.50,0.50,0.70,0.87,0.87,0.80,0.70,0.43,0.77,1.00,0.67,0.67,0.80,0.47,0.73,0.93,0.67,0.80,0.67,0.73,0.67
0.60,0.93,0.57,0.87,0.80,0.60,0.63,0.77,0.57,0.67,0.83,0.67,0.80,0.80,0.73,0.87,0.70,0.87,1.00,0.73,0.30,0.87,0.53,0.73,0.53,0.67,0.90,0.63,0.63,0.63
0.77,0.97,0.73,0.90,1.00,0.70,0.70,0.67,0.63,0.47,0.57,0.70,0.87,0.87,0.73,0.67,0.53,0.80,0.80,0.63,0.50,0.77,0.47,0.73,0.93,0.67,0.80,0.67,0.77,0.67
0.83,0.97,0.67,0.93,0.90,0.63,0.67,0.73,0.67,0.50,0.87,0.73,0.83,0.80,0.73,0.83,0.73,0.83,1.00,0.73,0.23,0.87,0.37,0.70,0.47,0.63,0.83,0.70,0.63,0.73
0.33,0.90,0.50,0.83,0.57,0.60,0.60,0.70,0.50,0.57,0.83,0.33,0.80,0.73,0.77,0.93,0.77,0.73,1.00,0.67,0.30,0.80,0.60,0.70,0.37,0.70,0.83,0.53,0.63,0.73
0.77,0.97,0.80,0.90,1.00,0.73,0.70,0.83,0.63,0.50,0.67,0.70,0.87,0.87,0.80,0.70,0.47,0.80,1.00,0.63,0.40,0.77,0.47,0.80,0.83,0.67,0.80,0.70,0.77,0.63
0.30,0.97,0.67,0.80,0.83,0.67,0.83,0.43,0.50,0.57,0.47,0.73,0.87,0.57,0.77,0.63,0.30,0.80,0.50,0.50,0.83,0.73,0.57,0.77,0.90,0.70,0.80,0.70,0.77,0.50
0.77,0.97,0.73,0.87,1.00,0.73,0.70,0.83,0.67,0.40,0.80,0.73,0.87,0.90,0.80,0.70,0.50,0.80,1.00,0.60,0.37,0.77,0.47,0.80,0.80,0.63,0.80,0.70,0.77,0.60
0.80,0.77,0.77,0.93,0.90,0.57,0.70,0.87,0.63,0.40,0.77,0.77,0.83,0.80,0.60,0.63,0.73,0.80,1.00,0.73,0.30,0.80,0.50,0.67,0.70,0.70,0.83,0.70,0.77,0.77
0.77,0.97,0.73,0.67,0.97,0.60,0.73,0.67,0.60,0.47,0.43,0.70,0.87,0.90,0.60,0.63,0.37,0.77,0.60,0.50,0.70,0.73,0.50,0.77,0.87,0.73,0.80,0.63,0.73,0.60
0.20,0.90,0.47,0.73,0.70,0.70,0.63,0.43,0.57,0.50,0.43,0.67,0.87,0.50,0.77,0.63,0.30,0.70,0.23,0.37,0.77,0.63,0.60,0.67,0.90,0.70,0.57,0.67,0.83,0.30
0.83,0.73,0.80,0.63,0.90,0.60,0.67,0.63,0.53,0.40,0.47,0.70,0.80,0.90,0.53,0.40,0.60,0.80,0.77,0.70,0.63,0.73,0.50,0.73,0.77,0.73,0.80,0.70,0.70,0.80
0.83,0.97,0.70,0.93,0.97,0.67,0.67,0.70,0.77,0.40,0.80,0.73,0.90,0.80,0.67,0.80,0.70,0.80,1.00,0.67,0.27,0.80,0.40,0.73,0.57,0.63,0.83,0.73,0.80,0.67
0.83,0.97,0.70,0.90,1.00,0.63,0.77,0.63,0.70,0.43,0.53,0.67,0.90,0.83,0.43,0.40,0.33,0.73,0.40,0.40,0.57,0.67,0.43,0.67,0.77,0.67,0.80,0.80,0.83,0.37
0.87,0.97,0.70,0.97,0.97,0.47,0.60,0.73,0.73,0.37,0.57,0.67,0.87,0.83,0.37,0.43,0.67,0.70,0.77,0.50,0.23,0.73,0.37,0.70,0.47,0.67,0.83,0.77,0.80,0.43
0.70,0.73,0.77,0.93,0.83,0.60,0.60,0.77,0.47,0.60,0.80,0.73,0.77,0.77,0.73,0.73,0.70,0.77,1.00,0.73,0.37,0.73,0.63,0.70,0.80,0.63,0.80,0.60,0.80,0.80
```

The heat map:

![testing-multiple2 heat map](data:image/png;base64,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)

Also checking to see how many of the programs are unique using the checksums
created during the `pgo_compile.sh` process:

```bash
cd /testing-multiple
/regalloc-testing/scripts/multiple/combined_regalloc.sh checksums.txt checksums.txt
cat checksums.txt | grep -o "^\w*" | uniq | wc -l
# output is 930 out of a possible high of 930
cd /testing-multiple2
/regalloc-testing/scripts/multiple/combined_regalloc.sh
cat checksums.txt | grep -o "^\w*" | uniq | wc -l
# output is 827 out of a possible high of 930
cd /
cat /testing-multiple/checksums.txt > checksums.txt
cat /testing-multiple2/checksums.txt >> checksums.txt
cat checksums.txt | grep -o "^\w*" | uniq | wc -l
# output is 1757 out of a possible high of 1860
```

So not all of the binaries are unique, but we have a pretty wide selection
of unique binaries.

### Discussion

Give the heatmaps shown and the performance in one direction on the sample
groups (going from the model produced with `testing-multiple2` to evaluting
it on `testing-multiple`), it seems like one model isn't necessarily that
applicable to another sample even given a fairly large training set. This
seems to imply that there is some large variable that is getting missed
in the inputs to the cost model that is also contributing significantly
to the variability in the data.

### Limitations

One of the metrics that I'm using here in evaluating models, particularly
the average difference between the predicted percent speedup/slowdown and
the actual speedup/slowdown is not great, because it is dependent pretty
heavily on the intercept of the model, which changes from model to model.
This is something that needs to be looked at in the future and adjusted.
Just looking at the polarity correct and average difference doesn't tell
us *when* the model is wrong though. If the model is wrong when the
slowdown or speedup is significant, that is way worse than if the model
is wrong when the speedup or slowdown is extremely small. Perhaps a
weighted average might be good here?

Within these experiments I was also producing different coefficients
for both stores and loads, but given the nature of these instructions
they have an extremely high degree of colinearity which can interfere
with the linear regression process. This does need to be fixed, but
running a couple quick tests it doesn't seem to impact the conclusions
at all.

### Conclusion

I think it is safe to conclude that the optimal model from sample to sample
varies significantly which implies that there is a major variable we aren't
taking into account. How bad this problem ends up beig in practice while
training ML models is hard to state though.

This also means that the question of whether or not we need to refit
the model for different programs becomes somewhat irrelevant because
it looks like we need to refit the model for every sample (ie
training batch) for optimal performance.

### Future Directions

* Work on better metrics for quantifying how significant this problem is
* Make scripts use adjusted R^2 (won't change conclusions at all, but is
good statistical practice).
* Try and find out what variables we aren't account for (could do a
search by emitting IR/assembly and looking for the fewest number
of lines changed relative to the highest difference between the
predicted and actual speedup).
* Hope that all of this data and my conclusions actually are correct
and aren't just complete crap