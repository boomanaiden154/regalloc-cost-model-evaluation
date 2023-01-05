# This script is designed to extract certain results from each sample of a
# collection
# Usage:
# fit_weights_extraction.sh <output type> <output file>
# The output type is the type of data to grab. Run scripts/fit_weighs.py to
# see possible values.
set -e
for i in {1..30}
do
    echo "working on iteration $i"
    cd iteration-$i
    value=$(python3 /regalloc-testing/scripts/fit_weights.py --input_file=test-combined.txt --output=$1)
    echo ${value##$1} >> ../$2
    cd ..
done
