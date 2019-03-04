#!/bin/sh

OUTPUT=`hadoop fs -ls /user/cloudera/outputAssignment1 2>&1`
if [ "$OUTPUT" !~ "No such file or directory" ]
then
    hadoop fs -rm -r /user/cloudera/outputAssignment1
    if [ "$?" != "0" ]
    then
        echo "Failed to remove the output directory in HDFS. Exiting..."
        exit 1
    fi
fi

hadoop jar /usr/lib/hadoop-0.20-mapreduce/contrib/streaming/hadoop-streaming-2.6.0-mr1-cdh5.12.0.jar -file mapper.py -mapper mapper.py -file reducer.py -reducer reducer.py -input /user/cloudera/inputAssignment1 -output /user/cloudera/outputAssignment1
if [ "$?" != "0" ]
then
    echo "Failed to execute. Exiting..."
    exit 1
fi

hadoop fs -getmerge /user/cloudera/outputAssignment1/part-* /home/cloudera/index.csv
if [ "$?" != "0" ]
then
    echo "Failed to relocate the output of mapreduce. Exiting..."
    exit 1
fi

python convert_cvs_to_pickle.py
if [ "$?" != "0" ]
then
    echo "Failed to build inverted index. Exiting..."
    exit 1
fi