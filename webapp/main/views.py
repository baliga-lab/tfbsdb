from django.shortcuts import render_to_response
from models import *

def index(request):
    num_genes = Gene.objects.count()
    num_motifs = Motif.objects.count()
    num_tfbs = TFBS.objects.count()
    return render_to_response('index.html', locals())
