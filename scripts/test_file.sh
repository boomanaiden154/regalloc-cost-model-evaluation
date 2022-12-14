set -e

processExecutable () {
    /regalloc-testing/scripts/pgo_compile.sh $1 test-$2 /warmstart/saved_policy
    /regalloc-testing/scripts/benchmark.sh ./test-$2 test-$2.benchmark.txt $3
    python3 /regalloc-testing/scripts/regalloc_score_parsing.py test-$2.regallocscoring.txt call-counts.txt >> results.txt
    echo -n "," >> results.txt
    python3 /regalloc-testing/scripts/benchmark_average.py test-$2.benchmark.txt >> results.txt
}

count=31
if [ -n "${2}" ]
then
    count=$2
fi
threads=1
if [ -n "${THREAD_COUNT}" ]
then
    threads=$THREAD_COUNT
fi
/llvm-project/build/bin/clang $1 -O3 -DCALL_COUNT_INSTRUMENTATION -o test-call-count
./test-call-count > call-counts.txt
for (( i=1; i<=$count; i++ ))
do
    ((j=(j+1)%threads)) || wait
    processExecutable $1 $i $((i%threads)) &
done
wait
