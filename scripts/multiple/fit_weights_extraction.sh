# This script is designed to extract certain results from each sample of a
# collection
# Usage:
# fit_weights_extraction.sh <query> <output file>
# The query is used to grep the specific line that you want
set -e
for i in {1..30}
do
    echo "working on iteration $i"
    cd iteration-$i
    value=$(python3 /regalloc-testing/scripts/fit_weights.py test-combined.txt | grep "$1")
    echo ${value##$1} >> ../$2
    cd ..
done
