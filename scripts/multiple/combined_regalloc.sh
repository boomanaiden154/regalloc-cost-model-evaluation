# This script is designed to concatenate all of the regalloc results from
# a group of multiple samples.
# Usage:
# combined_regalloc_raw.sh <per sample input> <output file>
# per sample input: The file to use for input, either results.txt or
# test-combined.txt in most cases
set -e
for i in {1..30}
do
    cd iteration-$i
    cat $1 >> ../$2
    cd ..
done
