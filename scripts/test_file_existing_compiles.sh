# script usage is test_file_existing_compiles.sh <folder name of existing work from test_file.sh>
set -e

processExecutable () {
    /regalloc-testing/scripts/benchmark.sh $1/test-$2 test-$2.benchmark.txt $3
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
$1/test-call-count > call-counts.txt
for (( i=1; i<=$count; i++ ))
do
    ((j=(j+1)%threads)) || wait
    processExecutable $1 $i $((i%threads)) &
done
wait
# post process executable serially to avoid file access race conditions
for (( i=1; i<=$count; i++ ))
do
    cp $1/test-$i.regallocscoring.txt ./
    python3 /regalloc-testing/scripts/regalloc_score_parsing.py test-$i.regallocscoring.txt call-counts.txt >> results.txt
    echo -n "," >> results.txt
    python3 /regalloc-testing/scripts/benchmark_average.py test-$i.benchmark.txt >> results.txt
done
