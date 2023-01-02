# script usage is test_file_existing_compiles.sh <folder name of existing work from test_file.sh>
set -e
$1/test-call-count > call-counts.txt
for i in {1..31}
do
    /regalloc-testing/scripts/benchmark.sh $1/test-$i test-$i.benchmark.txt
    cp $1/test-$i.regallocscoring.txt ./
    python3 /regalloc-testing/scripts/regalloc_score_parsing.py test-$i.regallocscoring.txt call-counts.txt >> results.txt
    echo -n "," >> results.txt
    python3 /regalloc-testing/scripts/benchmark_average.py test-$i.benchmark.txt >> results.txt
done
