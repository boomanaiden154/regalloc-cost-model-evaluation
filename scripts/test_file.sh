for i in {1..30}
do
    /scripts/pgo_compile.sh test.cpp test-$i /warmstart-1/saved_policy
    /scripts/benchmark.sh ./test-$i test-$i.benchmark.txt
    python3 /scripts/regalloc_score_parsing.py test-$i.regallocscoring.txt >> results.txt
    echo -n "," >> results.txt
    python3 /scripts/benchmark_average.py test-$i.benchmark.txt >> results.txt
done