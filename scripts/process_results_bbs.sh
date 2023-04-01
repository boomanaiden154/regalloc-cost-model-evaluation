# script usage is as follows:
# process_results_bbs.sh <number of iterations>
# The iteration count is optional
set -e

count=31
if [ -n "${2}" ]
then
    count=$2
fi

for (( i=1; i<=$count; i++))
do
    python3 /regalloc-testing/scripts/process_bbs.py test-$i test-$i.profiledump >> results_bbs.txt
    echo -n "," >> results_bbs.txt
    python3 /regalloc-testing/scripts/benchmark_average.py test-$i.benchmark.txt >> results_bbs.txt
    echo "finished processing test-$i"
done