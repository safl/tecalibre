#!/usr/bin/env python
#
#   Mymei  -   Pronounces "mighdy" as in "mighty" as in not at all :)
#           It is short for "My media-index".
#
#   I was tired of: picasa, xbmc and subsonic. I thought a simplistic
#   data index should not be a pain to implement...
#
#   * Multiuser, client/server
#   * Manage duplicates
#   * Webbased streaming client
#   * Backend with message-queue orientation
#   * Easy indexing or local-media / networked media
#   * Easy access to external media-sources such as DR-radio, DR-webtv
#
# Mymei cannot be bothered with every imaginable organisation of files.
# It is therefore assumed that data is organized as follow
#
# tv:
#
# /[path]/<tv name>(country) (year)/Season <number>/[whatever]<s01e01|S01E01|1x01|101>(title)(tags).<ext>
#
# Movies:
#
# /[path]/<movie name>(year)/[whatever](tags).<ext>
#
# Movie-Trailers:
#
# /[path]/<movie name>(year)/[whatever](tags)-trailer.<ext>
#
# Movie-Samples
#
# /[path]/<movie name>(year)/[whatever](tags)-sample.<ext>
#
#
# Thumbnails
#
# The object in question file-extension replaced with .tbn
#
import mimetypes
import logging
import pprint
import time
import glob
import re
import os

import pymongo

tvshow = {
    "name":     "",
    "network":  "",
    "art":      "",
    "fanart":   ""    
}

season = {
    "name":     "",
    "episodes": 0,
    "art":      ""
}

sources = [
    ('pictures',    '/home/safl/Desktop/projects/tecalibre/media/Pictures'),
    ('movies',      '/home/safl/Desktop/projects/tecalibre/media/Movies')
]

#
# File-types "supported" by indexer, this could also just be
# a direct strip from the mimetypes library, however leaving them
# here calls for an a "default-to-deny" such that only these
# whitelisted media-types are indexed.
#
# The lists could then be made user-definable.
#
audio_ext       = ['flac', 'wav', 'mp3']
audio_source    = ['cd', 'lp', 'web']
audio_quality   = ['lossless']

picture_ext     = ['jpg', 'jpeg']

video_ext       = ['mkv','ogv','ogg','avi','iso','img']
video_source    = ['webrip','hdtv','hdvd', 'hd','sd','tv','dvdrip', 'dvd9', 'dvd']
video_aformat   = ['stereo', 'ac3', 'dts', 'ws', 'extended', 'dubbed', 'german']
video_vformat   = ['xvid','720p','1080p', '(?:[a-z]+subs)', '(?:bluray|blu-ray)', '(?:web-dl|web dl|dl)', '(?:x 264|x-264|x264)','(?:h 264|h-264|h264)', '(?:dd5 1|dd5-1|dd51)','(?:aac2 0|aac2-0|aac20)']

#
# Regular Expressions matching media
#

picture_e_r = '(?P<ext>%s)$' % '|'.join(picture_ext)

# Matching video-file extensions such as .mkv, ogv etc.
video_e_r = '(?P<ext>%s)$' % '|'.join(video_ext)

# Matching tags-data 720p, hdtv, x264, extended, ws, dvdrip, web-dl etc.
video_m_r = '(?P<tags>%s)' % '|'.join(video_source+video_aformat+video_vformat)

# Matching season/episode info on the forms: S01E01, s01e01, 1x01, 111
tvshow_folder   = '(?P<name>.*?)(?P<country>\([a-z]{2}\))?\(?(?P<year>\d{4})?\)?'
season_folder   = 'Season (?P<season_folder>\d{1,2})'
series_r        = '(?:(?P<season>s[0-9]{2}|[0-9])(?P<episode>e[0-9]{2}|[0-9]{2}))'

tvshow_regex = os.sep+ \
    tvshow_folder +os.sep+ \
    season_folder +os.sep+ \
    '.*' +\
    series_r +\
    '.*' +\
    video_e_r

movie_regex = \
    os.sep+'.*?'+os.sep +\
    '(?P<name>.*?)(?P<country>\([a-z]{2}\))?\(?(?P<year>\d{4})?\)?' +\
    os.sep+'.*?' +\
    video_e_r

picture_meta = '(?P<tags>)'
picture_regex = \
    os.sep+'.*'+os.sep +\
    '(?P<name>.*?)' +\
    picture_e_r

media_types = {
    'tv': (tvshow_regex,  video_m_r),
    'movies':   (movie_regex,   video_m_r),
    'music':    (None, None),
    'books':    (None, None),
    'pictures': (picture_regex, picture_meta)
}

counts = dict(((k, 0) for k in media_types))

conn    = pymongo.Connection("localhost", 27017)
db      = conn.media

s = time.time()
for (media_type, source) in sources:
    
    for root, dirs, files in os.walk(source):
        
        for fp in files:
            
            parent_folders = root.split(os.sep)            
            subject = unicode(os.sep+ parent_folders[-2] +os.sep+ parent_folders[-1] +os.sep+ fp.lower().replace('.', ' ').replace('_',' '), 'utf-8')
            regex, meta_regex = media_types[media_type]
            
            media   = None
            m       = re.match(regex, subject)
            
            if m:
                
                counts[media_type] += 1
                m_meta  = [meta.replace('-','').replace(' ', '') for meta in re.findall(meta_regex, unicode(fp.lower(), 'utf-8'))]
                media   = m.groupdict()
                    
                media['name']   = media['name'].strip()
                media['tags']   = m_meta
                
                if 'year' in media:                    
                    media['year'] = int(media['year']) if media and media['year'] else None
                
                if media_type == 'tv':
                    
                    media['season']     = int(media['season'].replace('s',''))
                    media['episode']    = int(media['episode'].replace('e',''))
                    
                    # Unused... an error should be logged somewhere...
                    season_err = int(media['season_folder']) == media['season']
                    del(media['season_folder'])
                
                elif media_type == 'pictures':
                    media['tags'] = [t for t in root[len(source):].split("/") if t]                    
            
            if media:
                
                media['path'] = unicode(root +os.sep+ fp, 'utf-8')
                if media_type == 'movies':
                    print pprint.pprint(media)
                
                media['mimetype']   = mimetypes.guess_type(media['ext'].lower())
                media['meta']       = str(meta) if meta else ''
                db[media_type].save(media)

print counts
print time.time() -s
