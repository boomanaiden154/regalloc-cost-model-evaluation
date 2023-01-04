# designed to be run with no paramters in a directory with many subdirectories
# created by test_file_multiple.sh
set -e
for i in {1..30}
do
    echo "processing iteration-$i"
    cd iteration-$i
    /regalloc-testing/scripts/combined_regalloc_raw.sh test-combined.txt
    cd ..
done
