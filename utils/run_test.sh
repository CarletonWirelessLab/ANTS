#!/bin/bash
echo "Hello world"


#$1 name of the device
#$2 duration 
#$3 access category

python ./writeIQ.py $1 $2 $3
python3 ./top.py $1 $3
