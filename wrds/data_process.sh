#!/bin/bash
#$ -cwd
#$ -m abe
#$ -M yzhanggm@connect.ust.hk

echo "Starting job at `date`"

RESULT_FILE=result_info.txt

#if [ -fe $RESULT_FILE ]
#then
#    rm $RESULT_FILE
#fi

rm *.csv

~/miniconda3/bin/python3 ../codes/data_processor.py >> $RESULT_FILE

echo "Finished job at `date`"