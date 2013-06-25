from django.shortcuts import render_to_response
from django.utils import simplejson
from django.http import HttpResponse
from models import *

def index(request):
    num_genes = Gene.objects.count()
    num_motifs = Motif.objects.count()
    num_tfbs = TFBS.objects.count()
    return render_to_response('index.html', locals())

def search_tf(request):
    searchterm = request.GET.get('term', '')
    if searchterm:
        motifs = Motif.objects.filter(name=searchterm)
    
    return render_to_response('tf_results.html', locals())

def search_gene(request):
    searchterm = request.GET.get('term', '')
    if searchterm:
        try:
            entrez_id = int(searchterm)
            genes = Gene.objects.filter(name=entrez_id)
        except:
            genes = Gene.objects.none()

    return render_to_response('gene_results.html', locals())


def tf_completions(request):
    searchterm = request.GET.get('term', '')
    motifs = Motif.objects.filter(name__istartswith=searchterm)
    data = [m.name for m in motifs]
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

def gene_completions(request):
    data = ['g1', 'g2']
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')
