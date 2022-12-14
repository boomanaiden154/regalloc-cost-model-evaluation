for i in {1..30}
do
    /usr/bin/time -f'%E' $1 2>> $2
done
