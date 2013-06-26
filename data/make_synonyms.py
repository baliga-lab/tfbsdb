#!/usr/bin/python
"""
Synonym creator. Reads an EnsEMBL synonym file and adds the extracted
synonyms to the database
"""
import argparse
import psycopg2
import csv

if __name__ == '__main__':
    description = """synonym maker (c) 2013, Institute for Systems Biology"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--enssynfile', help='EnsEMBL synonym file',
                        required=True)
    args = parser.parse_args()
    conn = psycopg2.connect("dbname=tfbs user=dj_ango password=django")
    cursor = conn.cursor()
    cursor.execute('select id, name from main_gene')
    gene_map = { entrez_id: id
                 for id, entrez_id in cursor.fetchall()}

    synonyms = {}
    with open(args.enssynfile) as infile:
        reader = csv.reader(infile, delimiter=',', quotechar='"')
        lineno = 0
        for row in reader:
            if lineno > 0:
                entrez_id = row[2].strip()
                if entrez_id not in synonyms:
                    synonyms[entrez_id] = set()
                if len(entrez_id) > 0:
                    ensid = row[0].strip()
                    if len(ensid) > 0:
                        synonyms[entrez_id].add(ensid)

                    refseq = row[1].strip()
                    if len(refseq) > 0:
                        synonyms[entrez_id].add(refseq)

                    hgnc = row[4].strip()
                    if len(hgnc) > 0:
                        synonyms[entrez_id].add(hgnc)

            lineno += 1
        print "# entrez ids: ", len(synonyms)

        for entrez_id, entries in synonyms.items():
            if entrez_id in gene_map:
                for entry in entries:
                    cursor.execute("""insert into
main_genesynonyms (gene_id, name) values (%s, %s)
""", (gene_map[entrez_id], entry))
        conn.commit()
        conn.close()
        

