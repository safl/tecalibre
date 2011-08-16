from pymongo import Connection
import Image

import os

coll = Connection()['media']['pictures']

image_scales = [
    ('thumb',  (100,100)),
    ('small',   160),
    ('medium',  640),
    ('large',   1280)
]

def resize_lsma(img, size):
    """
    Resize img according to size.
    Size can either be (width, height) or an integer.
    When called with an integer the longest side of
    the image is set to size and the other side
    is scaled accordingly.
    """
    
    new_size = size
    if isinstance(size, int):
        w,h=img.size
        if w>h:
            ratio       = w/float(size)
            new_size    = ( size, int(h/ratio) )
        elif w<h:
            ratio       = h/float(size)            
            new_size    = ( int(w/ratio), size )
        else:
            new_size = (size, size)            
    
    return img.resize(new_size, Image.ANTIALIAS)

for media in coll.find():
    
    fn = media['path']
    if os.path.exists(fn):
        orig = Image.open(fn)
                
        for scale, size in image_scales:
            
            scaled_fn       = "%s.%s" % (fn,scale)
            if not scale in media:
                if not os.path.exists(scaled_fn):
                    scaled_image    = resize_lsma(orig, size)
                    scaled_image.save(scaled_fn, 'jpeg')
                
                media[scale] = scaled_fn
        
        coll.save(media)