echo "working on benchmarking $1"
for i in {1..30}
do
    echo "benchmarking iteration $i/30 for $1"
    { /usr/bin/time -f'%E' $1 >> /dev/null; } 2>> $2
done
