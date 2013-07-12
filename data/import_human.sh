#!/bin/bash

# This is a shell script to prepare data for jBrowse

JBROWSEDIR=/usr/share/nginx/html/jbrowse-human
DESTDIR=/usr/share/nginx/html/jbrowse-human/hsa-data
SRCDIR=~/tmp/hsa-input

if [ -d "$DESTDIR" ]
then
  echo "$DESTDIR exists, proceeding..."
else
  echo "$DESTDIR does not exist, creating..."
  mkdir $DESTDIR
fi
echo "Done. Importing genome..."

for f in $SRCDIR/*.fa ; do
  echo "prepare-refseqs.pl --fasta $f --out $DESTDIR" 
  $JBROWSEDIR/bin/prepare-refseqs.pl --fasta $f --out $DESTDIR
done

echo "Done. Importing GFF for binding sites..."

$JBROWSEDIR/bin/flatfile-to-json.pl --gff $SRCDIR/tfbs.gff --tracklabel tfbs --out $DESTDIR

echo "Done."