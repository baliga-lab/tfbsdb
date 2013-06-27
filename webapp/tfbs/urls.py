from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'main.views.index', name='index'),
    url(r'^searchtf$', 'main.views.search_tf', name='searchtf'),
    url(r'^searchgene$', 'main.views.search_gene', name='searchgene'),
    url(r'^viewtf/(?P<tfname>.*)$', 'main.views.view_tf', name='viewtf'),
    url(r'^viewgene/(?P<genename>.*)$', 'main.views.view_gene', name='viewgene'),

    url(r'^tfcompletions$', 'main.views.tf_completions', name='tfcomp'),
    url(r'^genecompletions$', 'main.views.gene_completions', name='genecomp'),

    url(r'^tfgenes_csv/(?P<tfname>.*)$', 'main.views.tfgenes_csv', name='tfgenes_csv'),

    # url(r'^tfbs/', include('tfbs.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
