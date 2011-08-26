#!/usr/bin/env python
from urllib import urlretrieve
import os

from hachoir_metadata import extractMetadata
from hachoir_parser import createParser
from pymongo import Connection
import Image

import tmdb

coll = Connection()['media']['movies']

movies_assocs = [
    ('poster',      ['jpg']),
    ('backdrop',    ['jpg']),
    ('trailer',     ['mov','avi','ogg','ogv','mp4','mkv'])
]

for movie in coll.find():
    
    if os.path.exists(movie['path']):
        
        dirname = os.path.dirname(movie['path'])
        fn, ext = os.path.splitext(os.path.basename(movie['path']))
        
        res = tmdb.search(movie['name'], movie['year'])

        ctx     = res[0] if len(res) >= 1 else None
        info    = tmdb.getInfo(ctx['id']) if ctx else None
        pt_url  = ctx['posters'][0]['image']['url'] if ctx and len(ctx['posters']) >= 1 else None
        bd_url  = ctx['backdrops'][0]['image']['url'] if ctx and len(ctx['backdrops']) >= 1 else None
        
        if ctx:                             # Update document and context
            
                                            # Grab file information
            #try:
                #    meta = extractMetadata(createParser(media['path']))
                #except KeyboardInterrupt:
                #    raise
                #
                #except:
                #    meta = None
                #    logging.debug("Failed grabbing meta.", exc_info=3)
            
            poster_name = None
            if pt_url:                      # Download poster
                poster_name = "%s%s%s-%s.%s" % (dirname, os.sep, fn, 'poster', 'jpg')                
                urlretrieve(pt_url, poster_name)
                movie['poster'] = poster_name
            
            backdrop_name = None
            if bd_url:                      # Download backdrop
                backdrop_name = "%s%s%s-%s.%s" % (dirname, os.sep, fn, 'backdrop', 'jpg')
                urlretrieve(bd_url, backdrop_name)
                movie['backdrop'] = backdrop_name
            
            movie['rating']         = ctx['rating'] # Update document
            movie['certification']  = ctx['certification']
            movie['overview']       = ctx['overview']
            movie['tagline']        = info['tagline']
            movie['runtime']        = info['runtime']
            movie['genres']         = [item['name'] for item in info['genres']]
            
            coll.save(movie)                # Store updates