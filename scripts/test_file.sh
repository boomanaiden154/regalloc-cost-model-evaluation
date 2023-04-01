# script usage is as follows:
# test_file.sh <file to test> <number of iterations to run>
# The second argument (number of iterations to run) is optional.
set -e

processExecutable () {
    /regalloc-testing/scripts/pgo_compile.sh $1 test-$2
    /regalloc-testing/scripts/benchmark.sh ./test-$2 test-$2.benchmark.txt $3
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
    # ensure that everything is offset by at least 1ms
    sleep 0.001
done
wait
