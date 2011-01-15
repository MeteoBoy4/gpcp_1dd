#!/bin/bash

FTP_BASE=ftp://meso.gsfc.nasa.gov/pub/1dd-v1.1
FILE_BASE=gpcp_1dd_v1.1_p1d.

function load_year {
   year=$1
   curl $FTP_BASE/$FILE_BASE${year}0[1-9].gz -o $FILE_BASE${year}0#1.gz
   curl $FTP_BASE/$FILE_BASE${year}1[0-2].gz -o $FILE_BASE${year}1#1.gz
}

for YEAR in 2002 2003 2004 2005 2006; do
   echo "Downloading $YEAR"
   load_year $YEAR
done

exit

# Unzip all
for GZIPFILE in $(ls $FILE_BASE*.gz); do
  echo "Unzipping: $GZIPFILE"
  gunzip $GZIPFILE
done
