#!/bin/bash

FILE_BASE=gpcp_1dd_v1.1_p1d.

# Unzip all
for GZIPFILE in $(ls $FILE_BASE*.gz); do
  echo "Unzipping: $GZIPFILE"
  gunzip $GZIPFILE
done
