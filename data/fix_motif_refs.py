#!/usr/bin/env python
import argparse
import sys
import psycopg2
import os, os.path


COLON_NAMES = [
    "RXRA::VDR_MA0074.1",
    "NFE2L1::MafG_MA0089.1",
    "Ddit3::Cebpa_MA0019.1",
    "HIF1A::ARNT_MA0259.1",
    "Arnt::Ahr_MA0006.1",
    "TLX1::NFIC_MA0119.1",
    "Hand1::Tcfe2a_MA0092.1",
    "PPARG::RXRA_MA0065.2",
    "NR1H2::RXRA_MA0115.1",
    "TAL1::TCF3_MA0091.1",
    "MYC::MAX_MA0059.1",
    "Tal1::Gata1_MA0140.1",
    "RXR::RAR_DR5_MA0159.1",
    "V$RXR::RAR_01_M02272",
    "V$TAL1::GATA1_01_M02243"
    ]


class MotifInstance:
    def __init__(self, orientation, location, pvalue, seqmatch, overlap):
        self.orientation = orientation
        self.location = location
        self.pvalue = float(pvalue)
        self.seqmatch = seqmatch
        self.overlap = overlap

    def __str__(self):
        return "motif(%s, %s, %f %s)" % (self.orientation,
                                         str(self.location),
                                         self.pvalue,
                                         self.seqmatch)

    def __repr__(self):
        return str(self)


def make_range(value):
    comps = value.split('-')
    return (int(comps[0]), int(comps[1]))


def make_hit(line):
    try:
        comps = line.strip().split(',')
        num_motifs = int(comps[3])

        mlocs = [make_range(r) for r in comps[4].split(';')]
        mors = comps[5].split(';')
        mpvals = comps[6].split(';')
        mseqs = comps[7].split(';')
        overlaps = map(int, comps[8].split(';'))

        return {
            'entrezid': comps[0],
            'promoter': make_range(comps[1]),
            'chromosome': comps[2],
            'motif_instances': [MotifInstance(mors[i], mlocs[i],
                                              mpvals[i], mseqs[i],
                                              overlaps[i])
                                for i in range(num_motifs)]
            }
    except:
        print "error in line: '%s'" % line
        raise


def process_motif(cursor, path, motif_name, gene_map, motif_map):
    print "processing motif: ", motif_name, "..."
    motif_id = motif_map[motif_name]
    with open(path) as infile:
        header = infile.readline()
        num_processed = 0
        for line in infile:
            line = line.strip()
            if len(line) > 0:
                hit = make_hit(line)
                entrez_id = hit['entrezid']
                if entrez_id not in gene_map:
                    print "adding missing gene '%s'" % entrez_id
                    cursor.execute('insert into main_gene (name,description,chromosome,start_promoter,stop_promoter,tss,orientation) values (%s,%s,%s,%s,%s,%s,%s) returning id',
                                   [entrez_id, '', hit['chromosome'],
                                    hit['promoter'][0], hit['promoter'][1],
                                    0, '+'])
                    gene_map[entrez_id] = cursor.fetchone()[0]

                gene_id = gene_map[entrez_id]
                minstances = hit['motif_instances']
                for i in minstances:
                    cursor.execute("""insert into
main_tfbs (gene_id, motif_id, start, stop, orientation,
p_value, match_sequence, overlap_with_footprints) values (%s, %s, %s, %s, %s, %s, %s, %s)
""", (gene_id, motif_id, i.location[0], i.location[1], i.orientation, i.pvalue, i.seqmatch, i.overlap))
                num_processed += 1
        if num_processed == 0:
            print "motif '%s' was ignored - no hits" % (motif_name)


def process_genehits(conn, genehitdir, gene_map, motif_map):
    cursor = conn.cursor()
    for filename in os.listdir(genehitdir):
        motif_name = filename.replace('fullGenome_motifHits_', '').replace(
            '.csv', '')
        #print "motif: ", motif_name
        if motif_name in motif_map:
            #process_motif(cursor, genehitdir, gene_map, motif_map, motif_name)
            pass
        else:
            print "not found: ", motif_name

    print "\ndone."


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

    cursor.execute('select id, name from main_motif where id not in (select distinct motif_id from main_tfbs)')
    missing_motif_map = { name: id
                          for id, name in cursor.fetchall()}
    print "missing motif references: ", len(missing_motif_map)

    colon_names = {name.replace('::', '_').replace('$', '_'): name.replace('::', '').replace('$', '_')
                   for name in COLON_NAMES}

    # Try to find the missing motif name in the hit directory
    for motif_name in missing_motif_map.keys():
        path = os.path.join(args.genehitdir, 'fullGenome_motifHits_%s.csv' % motif_name)
        if os.path.exists(path):
            process_motif(cursor, path, motif_name, gene_map, missing_motif_map)
            conn.commit()
            #print "make motif: ", motif_name
        else:
            if motif_name in colon_names:
                alt_name = colon_names[motif_name]
                #print "not found (but a colon name): ", path
                path = os.path.join(args.genehitdir, 'fullGenome_motifHits_%s.csv' % alt_name)
                if os.path.exists(path):
                    process_motif(cursor, path, motif_name, gene_map, missing_motif_map)
                    conn.commit()
                    #print "make motif: ", motif_name
                else:
                    print "SCREWED UP: ", path
            else:
                print "not found (and not a colon name): ", path

    conn.close()
