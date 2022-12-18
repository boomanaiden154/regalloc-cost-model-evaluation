# script to parse all regalloc results (raw form) into a single file
# ./combined_regalloc_raw.sh <output file>
set -e
for i in {1..31}
do
    cat test-$i.regallocscoring.txt | tr -d '\n' >> $1
    echo -n "," >> $1
    python3 /regalloc-testing/scripts/benchmark_average.py test-$i.benchmark.txt >> $1
done
