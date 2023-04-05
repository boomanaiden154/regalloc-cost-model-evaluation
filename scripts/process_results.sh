# script usage is as follows:
# process_results.sh <number of iterations>
# the iteration count is optional
set -e

count=31
if [ -n "${2}" ]
then
    count=$2
fi

for (( i=1; i<=$count; i++))
do
    python3 /regalloc-testing/scripts/regalloc_score_parsing.py test-$i.regallocscoring.txt call-counts.txt >> results.txt
    echo -n "," >> results.txt
    python3 /regalloc-testing/scripts/benchmark_average.py --input_file=test-$i.benchmark.txt >> results.txt
    python3 /regalloc-testing/scripts/benchmark_average.py --input_file=test-$i.benchmark.txt --noaverage --stdev >> results_stdev.txt
done
