#!/usr/bin/python
import argparse
import psycopg2

if __name__ == '__main__':
    description = """gene_gff (c) 2013, Institute for Systems Biology"""
    print "##gff-version 3"
    conn = psycopg2.connect("dbname=tfbs user=dj_ango password=django")
    cursor = conn.cursor()
    cursor.execute("""select g.chromosome, g.orientation, g.start_promoter,
g.stop_promoter, s.name from main_gene g join (select gene_id, name from main_genesynonyms where synonym_type='hgnc') s on g.id = s.gene_id""")

    for chrom, strand, start, stop, name in cursor.fetchall():
        print "%s\t.\tgene\t%d\t%d\t.\t%s\t.\tName=%s" % (chrom,
                                                          start,
                                                          stop,
                                                          strand,
                                                          name)
