from django.shortcuts import render_to_response
from django.utils import simplejson
from django.http import HttpResponse
from django.db.models import Count
from models import *
import re

def index(request):
    num_genes = Gene.objects.count()
    num_motifs = Motif.objects.count()
    num_tfbs = TFBS.objects.count()
    return render_to_response('index.html', locals())

def search_tf(request):
    searchterm = request.GET.get('term', '')
    if searchterm:
        motifs = Motif.objects.filter(name=searchterm)
        m = motifs[0]
        tfbs = TFBS.objects.filter(motif__id=1).values(
            'gene__name',
            'gene__chromosome',
            'gene__start_promoter',
            'gene__stop_promoter',
            'gene__tss').annotate(num_sites=Count('motif'))
    return render_to_response('tf_results.html', locals())

def search_gene(request):
    searchterm = request.GET.get('term', '')
    if searchterm:
        try:
            entrez_id = int(searchterm)
            genes = Gene.objects.filter(name=entrez_id)
        except:
            genes = Gene.objects.filter(genesynonyms__name=searchterm)
    if genes.count() > 0:
        gene = genes[0]
    return render_to_response('gene_results.html', locals())


def tf_completions(request):
    searchterm = request.GET.get('term', '')
    motifs = Motif.objects.filter(name__istartswith=searchterm)
    data = [m.name for m in motifs]
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

# Everything that starts with ENSGxxxx will naturally return tons of results
# make sure we avoid returning huge lists
ENSG_PAT = re.compile('^(en?s?g?$)|(ensg\d*$)', re.IGNORECASE)

def gene_completions(request):
    searchterm = request.GET.get('term', '')
    try:
        n = int(searchterm)
        genes = Gene.objects.filter(name__startswith=searchterm)
        data = [g.name for g in genes]
    except:
        if not ENSG_PAT.match(searchterm) or len(searchterm) > 10:
            synonyms = GeneSynonyms.objects.filter(name__istartswith=searchterm)
            data = [s.name for s in synonyms]
        else:
            data = []
    print "# elems: ", len(data)
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')
