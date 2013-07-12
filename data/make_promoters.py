#!/usr/bin/python
import argparse
import sys
import os, os.path

"""
make_promoters.py

This script scans the gene hits directory and extracts a promoter file
out of the data.
"""

def process_genehits(genehitdir, strandmap):
    results = {}
    for filename in os.listdir(genehitdir):
        with open(os.path.join(genehitdir, filename)) as infile:
            header = infile.readline()
            for line in infile:
                if len(line.strip()) > 0:
                    try:
                        comps = line.strip().split(',')
                        entrez_id = comps[0]
                        prom = comps[1].split("-")
                        prom_start = int(prom[0])
                        prom_stop = int(prom[1])
                        chrom = comps[2]
                        if entrez_id in strand_map:
                            strand = strand_map[entrez_id]
                            results[entrez_id] = (chrom, strand, prom_start,
                                                  prom_stop)
                    except:
                        print "error in line: '%s'" % line
                        raise

    for entrez_id, data in results.items():
        chrom, strand, start, stop = data
        print "%s\t%s\t%s\t%d\t%d" % (entrez_id, chrom, strand,
                                      start, stop)


if __name__ == '__main__':
    description = """make_promoters.py (c) 2013, Institute for Systems Biology"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--genehitdir', help='gene hits directory',
                        required=True)
    parser.add_argument('--refpromoters', help='references promoters file',
                        required=True)
    args = parser.parse_args()
    strand_map = {}
    with open(args.refpromoters) as infile:
        infile.readline()
        for line in infile:
            comps = line.split('\t')
            strand_map[comps[0]] = comps[2]
    #print strand_map
    print "EntrezID\tChromosome\tStrand\tstart\tstop"
    process_genehits(args.genehitdir, strand_map)
