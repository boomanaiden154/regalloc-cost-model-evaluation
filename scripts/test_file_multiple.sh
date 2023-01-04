set -e
for i in {1..30}
do
    mkdir iteration-$i
    cd iteration-$i
    /regalloc-testing/scripts/test_file.sh $1
    cd ..
done
