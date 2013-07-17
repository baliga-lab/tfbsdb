#!/usr/bin/python
import argparse

if __name__ == '__main__':
    description = """gene_bed (c) 2013, Institute for Systems Biology"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--genefile', help='gene file',
                        required=True)
    args = parser.parse_args()
    with open(args.genefile) as infile:
        print 'track name=Promoters description="Promoters" useScore=1'
        for line in infile:
            comps = line.split('\t')
            name = comps[1]
            chrom = comps[2]
            strand = comps[3]
            start = int(comps[4])
            stop = int(comps[5])
            cds_start = int(comps[6])
            cds_end = int(comps[7])
            exon_count = int(comps[8])
            exon_starts = [int(n) for n in comps[9].split(',') if n]
            exon_ends = [int(n) for n in comps[10].split(',') if n]
            exon_sizes = [str(exon_ends[i] - exon_starts[i])
                          for i in range(exon_count)]
            score = float(comps[11])
            name2 = comps[12]
            print "%s\t%s\t%s\t%s\t%f\t%s\t%d\t%d\t0\t%d\t%s\t%s" % (
                chrom, start, stop, name2, score, strand,
                cds_start, cds_end, exon_count,
                ",".join(exon_sizes),
                ",".join(map(str, exon_starts)))
