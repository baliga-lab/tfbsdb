import base64
import json

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db.models import Count
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect

from models import *
import re


#############################################################################
#
def view_or_basicauth(view, request, test_func, realm = "", *args, **kwargs):
    """
    This is a helper function used by both 'logged_in_or_basicauth' and
    'has_perm_or_basicauth' that does the nitty of determining if they
    are already logged in or if they have provided proper http-authorization
    and returning the view if all goes well, otherwise responding with a 401.
    """
    if test_func(request.user):
        # Already logged in, just return the view.
        #
        return view(request, *args, **kwargs)

    # They are not logged in. See if they provided login credentials
    #
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        return view(request, *args, **kwargs)

    # Either they did not provide an authorization header or
    # something in the authorization attempt failed. Send a 401
    # back to them to ask them to authenticate.
    #
    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response
    
#############################################################################
#
def logged_in_or_basicauth(realm = ""):
    """
    A simple decorator that requires a user to be logged in. If they are not
    logged in the request is examined for a 'authorization' header.

    If the header is present it is tested for basic authentication and
    the user is logged in with the provided credentials.

    If the header is not present a http 401 is sent back to the
    requestor to provide credentials.

    The purpose of this is that in several django projects I have needed
    several specific views that need to support basic authentication, yet the
    web site as a whole used django's provided authentication.

    The uses for this are for urls that are access programmatically such as
    by rss feed readers, yet the view requires a user to be logged in. Many rss
    readers support supplying the authentication credentials via http basic
    auth (and they do NOT support a redirect to a form where they post a
    username/password.)

    Use is simple:

    @logged_in_or_basicauth
    def your_view:
        ...

    You can provide the name of the realm to ask for authentication within.
    """
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     lambda u: u.is_authenticated(),
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator

#############################################################################
#
def has_perm_or_basicauth(perm, realm = ""):
    """
    This is similar to the above decorator 'logged_in_or_basicauth'
    except that it requires the logged in user to have a specific
    permission.

    Use:

    @logged_in_or_basicauth('asforums.view_forumcollection')
    def your_view:
        ...

    """
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     lambda u: u.has_perm(perm),
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator

############################################################3

@logged_in_or_basicauth()
def index(request):
    num_genes = Gene.objects.count()
    num_motifs = Motif.objects.count()
    num_tfbs = TFBS.objects.count()
    return render_to_response('index.html', locals())

def notFound(request):
    badName = request.GET.get('badName', '')
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
    if len(motifs)==0:
        return HttpResponseRedirect('/notFound?badName='+tfname)
    tfbs_data = []
    motif = motifs[0]
    gene = Gene.objects.filter(motifs__name=motif.name).all()[0].hgnc
    # Compile based on genes
    tfbs = {}
    params = []
    for t1 in TFBS.objects.filter(motif__name=tfname):
        if not t1.gene.name in tfbs:
            tmp = GeneSynonyms.objects.filter(gene__name=t1.gene.name).filter(synonym_type='hgnc')
            symbol = '~'
            if len(tmp)>0:
                symbol = tmp[0].name
            tfbs[t1.gene.name] = { 'symbol':symbol, 'entrez':t1.gene.name, 'num_sites':1, 'chromosome':t1.gene.chromosome, 'strand':t1.gene.orientation, 'start':t1.gene.start_promoter, 'stop':t1.gene.stop_promoter, 'tss':t1.gene.tss }
        else:
            tfbs[t1.gene.name]['num_sites'] += 1
        params.append((t1.gene.name, t1.gene.orientation, t1.gene.tss, t1.gene.start_promoter, t1.gene.stop_promoter, t1.start, t1.stop))
    num_buckets = 30
    tfbs_data = tfbs.values()

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

    if len(genes) > 0:
        gene = genes[0]
    else:
        return HttpResponseRedirect('/notFound?badName='+genename)
    motifs = [motif.name for motif in gene.motifs.all() if len(TFBS.objects.filter(motif=motif).all())>0]
    return render_to_response('gene_results.html', locals())


def search_gene(request):
    searchterm = request.GET.get('searchterm', '')
    return view_gene(request, searchterm)

def tf_completions(request):
    searchterm = request.GET.get('term', '')
    data = [t.motif.name
            for t in TFBS.objects.filter(motif__name__icontains=searchterm).distinct('motif__name')]
    return HttpResponse(json.dumps(data), content_type='application/json')

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
            synonyms = GeneSynonyms.objects.filter(name__icontains=searchterm)
            data = [s.name for s in synonyms]
        else:
            data = []
    print "# elems: ", len(data)
    return HttpResponse(json.dumps(data), content_type='application/json')

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
        prom_start = int(t['gene__start_promoter'])
        prom_stop = int(t['gene__stop_promoter'])
        tss = int(t['gene__tss'])
        num_sites = int(t['num_sites'])

        result += "%s\t%s\t%s\t%s\t%s-%s\t%s\t%s\n" % (t['gene__name'],
                                                   ",".join(syns),
                                                   t['gene__chromosome'],
                                                   t['gene__orientation'],
                                                   str(prom_start), str(prom_stop),
                                                   str(tss), str(num_sites))

    resp = HttpResponse(result, content_type='application/csv')
    resp['Content-Disposition'] = 'attachment; filename="%s_genes.tsv"' % tfname
    return resp

def genetfbs_csv(request, genename):
    gene = Gene.objects.get(name=genename)
    result = "Motif\tStrand\tLocation\tp-value\tMatch Sequence\n"
    rows = ["%s\t%s\t%d-%d\t%f\t%s" % (t.motif.name,
                                       t.orientation,
                                       int(t.start), int(t.stop),
                                       t.p_value, t.match_sequence)
            for t in gene.tfbs_set.all()]
    result += "\n".join(rows)

    resp = HttpResponse(result, content_type='application/csv')
    resp['Content-Disposition'] = 'attachment; filename="%s_tfbs.tsv"' % genename
    return resp

def constructionValidation(request):
    return render_to_response('constructionValidation.html', locals())

def optimalPromoter(request):
    return render_to_response('optimalPromoterSize.html', locals())

def download(request):
    return render_to_response('download.html', locals())

def citationAndContact(request):
    return render_to_response('citationAndContact.html', locals())

