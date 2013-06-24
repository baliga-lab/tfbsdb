#!/usr/bin/python
import urllib2
import xml.etree.ElementTree as ET

EINFO_URL    = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi"
ESEARCH_URL  = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
ELINK_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
EFETCH_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def esummary(entrezid):
    """retrieves gene name and description for an entrez id"""
    url = "%s?db=gene&id=%d&version=2.0" % (ESUMMARY_URL, entrezid)
    resp = urllib2.urlopen(url)
    xmldoc = resp.read()
    summary = ET.fromstring(xmldoc)
    gname = ''
    gdesc = ''

    try:
        for elem in summary[0]:
            if elem.tag == 'DocumentSummary':
                for e in elem:
                    if e.tag == 'Name':
                        gname = e.text
                    elif e.tag == 'Description':
                        gdesc = e.text
    except:
        raise Exception('problem in gene %d' % entrezid)
                            
    return (gname, gdesc)
    

def efetch(entrezid):
    url = "%s?db=gene&id=%d&version=2.0&retmode=xml" % (EFETCH_URL, entrezid)
    resp = urllib2.urlopen(url)
    xmldoc = resp.read()
    doc = ET.fromstring(xmldoc)
    entrezgene = doc[0]


if __name__ == '__main__':
    print esummary(163782)
