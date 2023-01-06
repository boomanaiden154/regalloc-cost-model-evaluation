echo "working on benchmarking $1"
for i in {1..30}
do
    echo "benchmarking iteration $i/30 for $1"
    if [ -n "${3}" ]
    then
	{ /usr/bin/time -f'%E' taskset -c $3 $1 >> /dev/null; } 2>> $2
    else
        { /usr/bin/time -f'%E' $1 >> /dev/null; } 2>> $2
    fi
done
