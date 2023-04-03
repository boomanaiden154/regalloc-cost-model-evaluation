# designed to generate results.txt and results_bbs.txt files for all of the
# sample groups in a multisample environment
set -e
for i in {1..30}
do
    echo "processing iteration-$i"
    cd iteration-$i
    /regalloc-testing/scripts/process_results.sh
    /regalloc-testing/scripts/process_results_bbs.sh
    cd ..
done
/regalloc-testing/scripts/multiple/combined_regalloc.sh results.txt results.txt
/regalloc-testing/scripts/multiple/combined_regalloc.sh results_bbs.txt results_bbs.txt