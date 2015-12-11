# empty file so salib can be a module

from __future__ import print_function
import sys

import os
import os.path
try:
    import magic
    def mimetype(filename):
        return magic.from_file(filename,mime=True)
except ImportError:
    WARNED1 = False
    def mimetype(filename):
        global WARNED1
        if not WARNED1:
            print("Unable to import module 'magic'.  Image type will be guessed from extension.",file=sys.stderr)
            WARNED1 = True
        ext = filename.split('.')[-1]
        if ext == 'svg':
            return 'image/svg+xml'
        if ext == 'png':
            return 'image/png'
        if ext in ['jpeg','jpg']:
            return 'image/jpeg'
        return 'image/'+ext
        
from IPython import display

EXTS = ['svg','png','jpeg','jpg']

def showImage(basename,rescan=False):
    """Display an image whose basename is 'basename'.  If an image
    cannot be found, the user is asked to scan an image, which is
    then installed.  Extensions '.jpg', '.png', '.svg' are tried in
    that order.  If rescan is True, scanning a new image is forced."""

    def _display(ifile):
        itype = mimetype(ifile)
        img = None
        if itype in ['image/jpeg','image/png']:
            img = display.Image(filename=ifile,embed=True)
        elif itype == 'image/svg+xml':
            with file(ifile,"rb") as inf:
                svgdata = inf.read()
            img = display.SVG(data=svgdata)
        else:
            raise Exception("Invalid image type: {0}".format(itype))
        if img:
            display.display(img)

    if not rescan:
        if os.path.exists(basename):
            _display(basename)
            return
        for ext in EXTS:
            ifile = basename + '.' + ext
            if os.path.exists(ifile):
                _display(ifile)
                return
                
    ifile = basename + '.' + EXTS[-1]
    cmd = "scan-to-file {0}".format(ifile)
    os.system(cmd)
    if os.path.exists(ifile):
        _display(ifile)
    else:
        raise Exception("Unable to find image '{0}'; Tried these extensions: {1}".format(basename,EXTS))
