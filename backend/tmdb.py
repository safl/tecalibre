#!/usr/bin/env python
from urllib2 import urlopen
from urllib import quote_plus, urlretrieve
from json import loads

lang    = 'en'
marsh   = 'xml'
marsh_types = ['json', 'yaml', 'xml']

conf = {
    "apikey":   "3e7807c4a01f18298f64662b257d7059", # TODO: get a key!
}

def search(name, year=None):
    
    movie_name  = '%s %d' % (name, year) if year else name
    jsn         = urlopen(
        "http://api.themoviedb.org/2.1/Movie.search/en/json/%s/%s" % (
            conf['apikey'],
            quote_plus(movie_name)
        )
    )
    return loads(jsn.read())

r = search("The Terminator", 1984)