#!/bin/bash


FTP_BASE=ftp://meso.gsfc.nasa.gov/pub/1dd-v1.1
FILE=gpcp_1dd_v1.1_p1d.200801.gz

curl $FTP_BASE/$FILE -o $FILE

gunzip $FILE
