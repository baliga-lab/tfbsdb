#!/usr/bin/python
import pickle

pssm_pk = 1
motif_pk = 1

def process_motifs(filename, dbid):
    global pssm_pk, motif_pk
    with open(filename) as infile:
        motifs = pickle.load(infile)

    for index, motif_name in enumerate(motifs.keys()):
        motif = motifs[motif_name]
        print """  {
    "pk": %d,
    "model": "main.motif",
    "fields": {
      "source_database": %d,
      "name": "%s"
    }
  },""" % (motif_pk, dbid, motifs[motif_name].name)

        for index, row in enumerate(motif.matrix):
            print """  {
    "pk": %d,
    "model": "main.pssm",
    "fields": {
      "motif": %d,
      "index": %d,
      "a": %f,
      "c": %f,
      "g": %f,
      "t": %f
    }
  },""" % (pssm_pk, motif_pk, index, row[0], row[1], row[2], row[3])
            pssm_pk += 1
        motif_pk += 1

if __name__ == '__main__':
    print "["
    process_motifs("motifs/jasparCoreVertebrata.pkl", 1)
    process_motifs("motifs/selexPSSMsNonRedundant.pkl", 2)
    process_motifs("motifs/transfac_2012.1_PSSMs_vertabrate.pkl", 3)
    print "]\n"
