# empty file so salib can be a module

from __future__ import print_function
import sys

import os
import os.path
from IPython import display
import imghdr

def __test_svg(bstream,fileobj):
    """Extension for imghdr to detect svg files."""
    if fileobj:
        fileobj.seek(0)
        data = fileobj.read(6)
    else:
        data = bstream.read(6)
    if data == b'<?xml ':  # IFFY!
        return 'svg'
    return None
imghdr.tests.append(__test_svg)

EXTS = ['svg','png','jpeg','jpg']

def showImage(basename,rescan=False):
    """Display an image whose basename is 'basename'.  If an image
    cannot be found, the user is asked to scan an image, which is
    then installed.  Extensions '.jpg', '.png', '.svg' are tried in
    that order.  If rescan is True, scanning a new image is forced."""

    def _display(ifile):
        itype = imghdr.what(ifile)
        img = None
        if itype in ['jpeg','png']:
            img = display.Image(filename=ifile,embed=True)
        elif itype == 'svg':
            with open(ifile,"rb") as inf:
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
