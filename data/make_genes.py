#!/usr/bin/python
import cPickle
import argparse
import sys
import os, os.path
import entrez

"""
make_genes.py

This script takes as input an entrez-id -> promoter location file
which was generated out of a modified version of 

https://github.com/cplaisier/Sequence-Extractor

It will also query NCBI for a the gene description.

Using this information, a JSON file will be generated that serves
as a fixture for the Django gene model
"""
class Gene:
    def __init__(self, entrez_id, name, desc, chromosome,
                 strand, prom_start, prom_end):
        self.entrez_id = entrez_id
        self.name = name
        self.desc = desc
        self.chromosome = chromosome
        self.strand = strand
        self.prom_start = prom_start
        self.prom_end = prom_end
    
    def tss(self):
        if self.strand == '+' and self.prom_end > 0:
            return self.prom_end - 500
        elif self.strand == '-' and self.prom_start > 0:
            return self.prom_start + 500
        return 0

    def to_fixture(self, pk):
        return """  {
    "pk": %d,
    "model": "main.gene",
    "fields": {
      "name": "%d",
      "description": "%s",
      "chromosome": "%s",
      "start_promoter": %d,
      "stop_promoter": %d,
      "tss": %d,
      "orientation": "%s"
    }
  },""" % (pk, self.entrez_id, self.desc, self.chromosome, self.prom_start,
          self.prom_end, self.tss(), self.strand)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "Gene[%d, '%s', '%s', '%s', '%s', %d-%d -> %d]" % (self.entrez_id,
                                                                  self.name,
                                                                  self.desc,
                                                                  self.chromosome,
                                                                  self.strand,
                                                                  self.prom_start,
                                                                  self.prom_end,
                                                                  self.tss())

if __name__ == '__main__':
    description = """make_genes.py (c) 2013, Institute for Systems Biology"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--promfile', help='promoter map file',
                        required=True)
    args = parser.parse_args()

    prom_map = {}
    with open(args.promfile) as infile:
        header = infile.readline()
        for line in infile:
            comps = line.strip().split('\t')
            # entrez -> (chr, strand, start, stop)
            prom_map[int(comps[0])] = (comps[1], comps[2],
                                       int(comps[3]), int(comps[4]))
    
    entrez_ids = prom_map.keys()

    with open('genes.json', 'w') as outfile:
        outfile.write("[\n")
        for index, entrez_id in enumerate(entrez_ids):
            s = entrez.esummary(entrez_id)
            chrom, strand, start, stop = prom_map[entrez_id]
            gene = Gene(entrez_id, s[0], s[1],
                        chrom, strand, start, stop)
            outfile.write(gene.to_fixture(pk=index + 1))
        outfile.write("]\n")
