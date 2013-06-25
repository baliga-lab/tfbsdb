#!/usr/bin/python
import argparse
import sys
import psycopg2
import os, os.path


class MotifInfo:
    def __init__(self, orientation, location, pvalue, seqmatch):
        self.orientation = orientation
        self.location = location
        self.pvalue = float(pvalue)
        self.seqmatch = seqmatch

    def __str__(self):
        return "motif(%s, %s, %f %s)" % (self.orientation,
                                         str(self.location),
                                         self.pvalue,
                                         self.seqmatch)

    def __repr__(self):
        return str(self)

def process_genehits(conn, genehitdir, gene_map, motif_map):
    def make_range(value):
        comps = value.split('-')
        return (int(comps[0]), int(comps[1]))

    def make_gene(line):
        try:
            comps = line.strip().split(',')
            num_motifs = int(comps[3])

            mlocs = [make_range(r) for r in comps[4].split(';')]
            mors = comps[5].split(';')
            mpvals = comps[6].split(';')
            mseqs = comps[7].split(';')
            

            return {
                'entrezid': int(comps[0]),
                'promoter': make_range(comps[1]),
                'chromosome': comps[2],
                'motif_infos': [MotifInfo(mors[i], mlocs[i], mpvals[i], mseqs[i])
                                for i in range(num_motifs)]
                }
        except:
            print "error in line: '%s'" % line
            raise
        
    motif_infos = []
    for filename in os.listdir(genehitdir):
        motif_name = filename.replace('fullGenome_motifHits_', '').replace(
            '.csv', '')
        #print "motif: ", motif_name
        if not motif_name in motif_map:
            print "not found: ", motif_name
            
        """
        with open(os.path.join(genehitdir, filename)) as infile:
            header = infile.readline()
            data = [make_gene(line) for line in infile
                    if len(line.strip()) > 0]
            if len(data) > 0:
                motif_infos.extend(data)
        sys.stdout.write(".")  # indicate progress
        sys.stdout.flush()
        """
    print "\ndone."
    entrez_ids = set([info['entrezid'] for info in motif_infos])


if __name__ == '__main__':
    description = """TFBS setter (c) 2013, Institute for Systems Biology"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--genehitdir', help='gene hit directory',
                        required=True)
    args = parser.parse_args()
    conn = psycopg2.connect("dbname=tfbs user=dj_ango password=django")
    cursor = conn.cursor()
    cursor.execute('select id, name from main_gene')
    gene_map = { entrez_id: id
                 for id, entrez_id in cursor.fetchall()}

    cursor.execute('select id, name from main_motif')
    motif_map = { name: id
                 for id, name in cursor.fetchall()}

    process_genehits(conn, args.genehitdir, gene_map, motif_map)
    conn.close()
