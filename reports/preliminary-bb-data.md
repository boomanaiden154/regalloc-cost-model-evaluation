# Preliminary BB Cost Model Data

This will cover some of the initial data that I have gotten by applying a SOA
basic block cost model (uiCA) to trying to estimate the performance of programs
compiled with arbitrary evictions in the LLVM greedy register allocator. This
is mostly for more own reference in the future.

### Setup

This was done with the `fannkuch-redux-functions.c` benchmark with `EXTRA_FLAGS`
set to `-DALWAYS_INLINE`. I did use threading when running the benchmarks, this
time using both `isolcpus` to isolate CPUs from the scheduler and custom compiling
a kernel with access to `nohz_full` to further isolate individual kernels.
The setup was similar to last time, running `test-file-multiple.sh` with the
default settings and environment set up appropriately.

### Performance of linear model, no weight changes

```
polarity correct:485/929
average difference:0.031422619831870884
kendall's tau:0.4989523390675196
```

### Performance of linear model after new regression

```
Multivariable regression coefficients:[ 2.01468399e-01  5.77809628e-01  3.17633228e-01  1.89562241e-01
 -3.03437219e+06]
Multivariable regression intercept:84534516328513.69
Normalized coefficients:[1.0, 2.8679913702792548, 1.5765908198764038, 0.9409030998715925, -15061281.141538037]
Unadjusted R^2 value:0.01446755399303512
Post regression polarity correct:521
Post regression average difference:0.025297999740946382
Post regression kendall's tau:0.49743997544590784
```

### Performance of basic block cost model

```
polarity correct:668/929
average difference:0.02650165495508575
kendall's tau:0.5654872891144503
```

### Conclusions

It seems like the basic block cost models are definitely a somewhat promising
direction. They are already able to outperform even a linear model that has
had a regression performed directly on the dataset it is being evaluated on.
I expect the major bottleneck that we're still seeing in cost model performance
is due to the absence of modelling of cache misses. If we are able to add
this data in, I suspect the cost model would perform significantly better as the
benchmark that this data was collected from does have a significant number of
cache misses (both L1D and LLC), which will significantly impact the performance
of a BB cost model that expects all memory accessing operations to hit L1D
cache.
