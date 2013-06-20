from django.db import models

class Gene(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    chromosome = models.CharField(max_length=50)
    start_promoter = models.IntegerField()
    stop_promoter = models.IntegerField()
    tss = models.IntegerField()
    orientation = models.CharField(max_length=10)


# Create your models here.
class GeneSynonyms(models.Model):
    gene = models.ForeignKey(Gene)
    name = models.CharField(max_length=255)

class Motif(models.Model):
    name = models.CharField(max_length=50)
    source_database = models.CharField(max_length=256)


class PSSM(models.Model):
    motif = models.ForeignKey(Motif)
    index = models.IntegerField()
    a = models.FloatField()
    c = models.FloatField()
    g = models.FloatField()
    t = models.FloatField()
    
