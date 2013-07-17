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


def jbrowse(request):
    return render_to_response('jbrowse.html', locals())


class HistogramData:
    def __init__(self, minval, maxval, refval, data):
        self.minval = minval
        self.maxval = maxval
        self.refval = refval
        self.data = data


def view_tf(request, tfname):
    def compute_relpos(params):
        result = []
        for gene_name, strand, tss, start_prom, stop_prom, start, stop in params:
            middle = (stop - start) / 2
            if middle > 0:  # start < stop
                x = start + middle
            else:           # start > stop
                x = start - middle
            if strand == '+':
                dist = (stop_prom - 500) - x
                #if dist < -500:
                #    print "%s (%s) - sp: %d ep: %d x: %d" % (gene_name, strand, start_prom, stop_prom, x)
                if dist > 8000:
                    print "distance > 8000, gene: ", gene_name
                elif dist < -8000:
                    print "distance < -8000, gene: ", gene_name
                else:
                    result.append((stop_prom - 500) - x)
            else:
                dist = x - (start_prom + 500)
                #if dist < -500:
                #    print "%s (%s) - sp: %d ep: %d x: %d" % (gene_name, strand, start_prom, stop_prom, x)
                if dist > 8000:
                    print "distance > 8000, gene: ", gene_name
                elif dist < -8000:
                    print "distance < -8000, gene: ", gene_name
                else:
                    result.append(x - (start_prom + 500))
        return result

    motifs = Motif.objects.filter(name=tfname)
    if len(motifs) > 0:
        motif = motifs[0]
        tfbs = TFBS.objects.filter(motif__name=tfname).values(
            'gene__name',
            'gene__chromosome',
            'gene__orientation',
            'gene__start_promoter',
            'gene__stop_promoter',
            'gene__tss',
            'start', 'stop').annotate(num_sites=Count('motif'))
    num_buckets = 30
    params = [(t['gene__name'], t['gene__orientation'], t['gene__tss'],
               t['gene__start_promoter'], t['gene__stop_promoter'],
               t['start'], t['stop'])
              for t in tfbs]
    dists = sorted(compute_relpos(params))
    #dists.reverse()
    #print dists
    min_dist = min(dists) if len(dists) > 0 else 0
    max_dist = max(dists) if len(dists) > 0 else 0
    histogram_data = HistogramData(min_dist, max_dist, 0, dists)
    return render_to_response('tf_results.html', locals())
    

def search_tf(request):
    searchterm = request.GET.get('searchterm', '')
    return view_tf(request, searchterm)


def view_gene(request, genename):
    try:
        entrez_id = int(genename)
        genes = Gene.objects.filter(name=entrez_id)
    except:
        genes = Gene.objects.filter(genesynonyms__name=genename)

    if genes.count() > 0:
        gene = genes[0]
    return render_to_response('gene_results.html', locals())


def search_gene(request):
    searchterm = request.GET.get('searchterm', '')
    return view_gene(request, searchterm)

def tf_completions(request):
    searchterm = request.GET.get('term', '')
    data = [t.motif.name
            for t in TFBS.objects.filter(motif__name__istartswith=searchterm).distinct('motif__name')]
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

def tfgenes_csv(request, tfname):
    tfbs = TFBS.objects.filter(motif__name=tfname).values(
        'gene__name',
        'gene__chromosome',
        'gene__orientation',
        'gene__start_promoter',
        'gene__stop_promoter',
        'gene__tss').annotate(num_sites=Count('motif'))

    result = "Entrez Id\tSynonyms\tChromosome\tStrand\tLocation\tTSS\t# sites\n"
    for t in tfbs:
        syns = [s.name for s in
                GeneSynonyms.objects.filter(gene__name=t['gene__name'])]
        result += "%s\t%s\t%s\t%d-%d\t%d\t%d\n" % (t['gene__name'],
                                                   ",".join(syns),
                                                   t['gene__chromosome'],
                                                   t['gene__orientation'],
                                                   t['gene__start_promoter'],
                                                   t['gene__stop_promoter'],
                                                   t['gene__tss'],
                                                   t['num_sites'])

    resp = HttpResponse(result, mimetype='application/csv')
    resp['Content-Disposition'] = 'attachment; filename="%s_genes.tsv"' % tfname
    return resp

def genetfbs_csv(request, genename):
    gene = Gene.objects.get(name=genename)
    result = "Motif\tStrand\tLocation\tp-value\tMatch Sequence\n"
    rows = ["%s\t%s\t%d-%d\t%f\t%s" % (t.motif.name,
                                       t.orientation,
                                       t.start, t.stop,
                                       t.p_value, t.match_sequence)
            for t in gene.tfbs_set.all()]
    result += "\n".join(rows)

    resp = HttpResponse(result, mimetype='application/csv')
    resp['Content-Disposition'] = 'attachment; filename="%s_tfbs.tsv"' % genename
    return resp
