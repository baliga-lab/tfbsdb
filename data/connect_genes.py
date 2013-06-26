#!/usr/bin/python
import argparse
import sys
import psycopg2
import os, os.path


if __name__ == '__main__':
    description = """gene-motif connect (c) 2013, Institute for Systems Biology"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--connectfile', help='gene-motif file',
                        required=True)
    args = parser.parse_args()
    conn = psycopg2.connect("dbname=tfbs user=dj_ango password=django")
    with open(args.connectfile) as infile:
        infile.readline()
        rows = []
        for line in infile.readlines():
            comps = line.strip().split(',')
            # motif name, entrez id
            rows.append((comps[0], comps[2]))
    cursor = conn.cursor()

    cursor.execute('select id, name from main_gene')
    gene_map = { entrez_id: id
                 for id, entrez_id in cursor.fetchall()}

    cursor.execute('select id, name from main_motif')
    motif_map = { name: id
                 for id, name in cursor.fetchall()}

    for motif_name, entrez_id in rows:
        if (motif_name in motif_map.keys() and
            entrez_id in gene_map.keys()):
            gene_id = gene_map[entrez_id]
            motif_id = motif_map[motif_name]
            print "insert gene: %d -> motif: %d" % (gene_id, motif_id)
            cursor.execute("""insert into main_gene_motifs
(gene_id, motif_id) values (%s, %s)""", [gene_id, motif_id])
        """
        if motif_name not in motif_map.keys():
            print "motif not found: ", motif_name
        if entrez_id not in gene_map.keys():
            print "gene not found: ", entrez_id
        """
    conn.commit()
    conn.close()
