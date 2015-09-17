from django.db import models


class MotifDatabase(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50)


class Motif(models.Model):
    source_database = models.ForeignKey(MotifDatabase, related_name='+')
    name = models.CharField(max_length=50, db_index=True)


class PSSM(models.Model):
    motif = models.ForeignKey(Motif)
    index = models.IntegerField()
    a = models.DecimalField(max_digits=8, decimal_places=6)
    c = models.DecimalField(max_digits=8, decimal_places=6)
    g = models.DecimalField(max_digits=8, decimal_places=6)
    t = models.DecimalField(max_digits=8, decimal_places=6)


class Gene(models.Model):
    motifs = models.ManyToManyField(Motif)
    name = models.CharField(max_length=15, db_index=True)
    description = models.CharField(max_length=1000)
    chromosome = models.CharField(max_length=50)
    start_promoter = models.IntegerField()
    stop_promoter = models.IntegerField()
    tss = models.IntegerField()
    orientation = models.CharField(max_length=1)

    def hgnc(self):
        synonyms = self.genesynonyms_set.filter(synonym_type='hgnc')
        return synonyms[0].name if synonyms.count() > 0 else ''

class GeneSynonyms(models.Model):
    gene = models.ForeignKey(Gene)
    name = models.CharField(max_length=255, db_index=True)
    synonym_type = models.CharField(max_length=30, db_index=True)


class TFBS(models.Model):
    gene = models.ForeignKey(Gene)
    motif = models.ForeignKey(Motif)
    start = models.IntegerField()
    stop = models.IntegerField()
    orientation = models.CharField(max_length=1)
    p_value = models.DecimalField(max_digits=8, decimal_places=6)
    match_sequence = models.CharField(max_length=256)
    overlap_with_footprints = models.IntegerField()
