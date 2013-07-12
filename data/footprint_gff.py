#!/usr/bin/python
import argparse

def process_combined(filename):
    with open(filename) as infile:
        with open('combined.gff', 'w') as outfile:
            outfile.write("##gff-version 3\n")
            for line in infile:
                chrom, start, stop = line.strip().split('\t')
                outfile.write("%s\t.\tnuclease_sensitive_site\t%s\t%s\t.\t.\t.\t.\n" % (chrom,
                                                                                        start,
                                                                                        stop))
            

def process_all(filename):
    tracks = {}
    with open(filename) as infile:
        for line in infile:
            chrom, start, stop, cellline, pval = line.strip().split('\t')
            with open('%s.gff' % cellline, 'a') as outfile:
                if cellline not in tracks:
                    outfile.write("##gff-version 3\n")
                    tracks[cellline] = True
                else:
                    outfile.write("%s\t.\tnuclease_sensitive_site\t%s\t%s\t%s\t.\t.\t.\n" % (chrom,
                                                                                             start,
                                                                                             stop,
                                                                                             pval))

if __name__ == '__main__':
    description = """footprint_gff (c) 2013, Institute for Systems Biology"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--fpfile', help='footprint file',
                        required=True)
    args = parser.parse_args()
    with open(args.fpfile) as infile:
        line = infile.readline()
        comps = line.split('\t')
        num_cols = len(comps)
        if num_cols == 3:
            process_combined(args.fpfile)
        elif num_cols == 5:
            process_all(args.fpfile)
