# script to parse all regalloc results (raw form) into a single file
# ./combined_regalloc_raw.sh <output file>
set -e
for i in {1..31}
do
    python3 /regalloc-testing/scripts/regalloc_sum_scores.py test-$i.regallocscoring.txt call-counts.txt | tr -d '\n' >> $1
    echo -n "," >> $1
    python3 /regalloc-testing/scripts/benchmark_average.py test-$i.benchmark.txt >> $1
done
