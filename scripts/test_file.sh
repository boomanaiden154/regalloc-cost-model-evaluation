set -e
/llvm-project/build/bin/clang $1 -O3 -DCALL_COUNT_INSTRUMENTATION -o test-call-count
./test-call-count > call-counts.txt
for i in {1..31}
do
    /regalloc-testing/scripts/pgo_compile.sh $1 test-$i /warmstart/saved_policy
    /regalloc-testing/scripts/benchmark.sh ./test-$i test-$i.benchmark.txt
    python3 /regalloc-testing/scripts/regalloc_score_parsing.py test-$i.regallocscoring.txt call-counts.txt >> results.txt
    echo -n "," >> results.txt
    python3 /regalloc-testing/scripts/benchmark_average.py test-$i.benchmark.txt >> results.txt
done
