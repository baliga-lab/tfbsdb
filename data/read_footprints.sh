#!/bin/bash

JBROWSEDIR=/usr/share/nginx/html/jbrowse-human
DESTDIR=$JBROWSEDIR/hsa-data
SRCDIR=~/tmp/hsa-input

for f in $SRCDIR/footprints/*.gff ; do
    filename="${f##*/}"
    #extension="${filename##*.}"
    filename="${filename%.*}"

    echo "flatfile-to-json.pl --gff $f --tracklabel $filename --out $DESTDIR"
    $JBROWSEDIR/bin/flatfile-to-json.pl --gff "$f" --tracklabel "$filename" --out $DESTDIR
done