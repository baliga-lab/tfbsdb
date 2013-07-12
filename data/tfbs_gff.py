#!/usr/bin/python
import argparse
import psycopg2

if __name__ == '__main__':
    description = """tfbs_gff (c) 2013, Institute for Systems Biology"""
    print "##gff-version 3"
    conn = psycopg2.connect("dbname=tfbs user=dj_ango password=django")
    cursor = conn.cursor()
    cursor.execute("""select g.chromosome, t.start, t.stop, t.p_value, t.orientation, m.name from main_gene g join main_tfbs t on g.id = t.gene_id join main_motif m on m.id = t.motif_id""")
    for chrom, start, stop, pval, strand, name in cursor.fetchall():
        print "%s\t.\tTF_binding_site\t%d\t%d\t%f\t%s\t.\tName=%s" % (chrom,
                                                                      start,
                                                                      stop,
                                                                      pval,
                                                                      strand,
                                                                      name)
